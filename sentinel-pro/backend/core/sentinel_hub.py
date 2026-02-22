import socketio
import asyncio
import time
import json
from engine.shared_state import state
from sqlalchemy import select
from .serial_bridge import ArduinoBridge
from backend.api.deps import AsyncSessionLocal
from backend.db.models import CrowdLog, SystemConfig, DetectionLog, Calibration, Zone

class SentinelHub:
    def __init__(self):
        self.sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
        self.app = socketio.ASGIApp(self.sio)
        self.arduino = ArduinoBridge()
        self.last_log_time = time.time()
        
        # Engines (Lazy loaded or init here)
        from engine.vision.vision_module import VisionEngine
        from engine.audio.audio_module import AudioEngine
        
        self.vision_engine = VisionEngine(source=None) # Use env var or default to 0
        self.audio_engine = AudioEngine()

    async def start_engines(self):
        print("[Hub] Starting Engines...")
        
        # Load calibration from DB
        try:
            async with AsyncSessionLocal() as session:
                # Mission V7: Check for active calibration in new table first
                result = await session.execute(select(Calibration).where(Calibration.is_active == True))
                active_cal = result.scalar_one_or_none()
                if active_cal:
                    h_list = json.loads(active_cal.matrix)
                    self.update_homography_matrix(h_list)
                    print(f"[Hub] Loaded Active Calibration: {active_cal.name}")
                else:
                    # Fallback to legacy SystemConfig
                    result = await session.execute(select(SystemConfig).where(SystemConfig.key == "homography_matrix"))
                    entry = result.scalar_one_or_none()
                    if entry:
                        h_list = json.loads(entry.value)
                        self.update_homography_matrix(h_list)
                        print("[Hub] Loaded Legacy Calibration from DB")
        except Exception as e:
            print(f"[Hub] Error loading calibration: {e}")

        if not self.vision_engine.is_alive():
            self.vision_engine.start()
        if not self.audio_engine.is_alive():
            self.audio_engine.start()

    def stop_engines(self):
        print("[Hub] Stopping Engines...")
        if self.vision_engine:
            self.vision_engine.stop()
            self.vision_engine.join()
        if self.audio_engine:
            self.audio_engine.stop()
            self.audio_engine.join()

    def update_homography_matrix(self, matrix):
        """Update vision engine with new homography matrix"""
        if self.vision_engine:
            self.vision_engine.set_homography(matrix)
            print("[Hub] Homography updated in Vision Engine")

    async def monitor_loop(self):
        print("[Hub] Monitor Loop Started")
        while True:
            # Mission V11: Sync Active Zones to State for Vision Engine PiP
            try:
                async with AsyncSessionLocal() as session:
                    result = await session.execute(select(Zone))
                    zone_list = result.scalars().all()
                    state.active_zones = [{"name": z.name, "polygon_data": z.polygon_data, "capacity": z.capacity, "alert_threshold": z.alert_threshold} for z in zone_list]
            except Exception as e:
                print(f"[Hub] Zone Sync Error: {e}")

            snapshot = state.get_snapshot()
            
            # Anomaly Alert Logic (Compare current vs 5-min average)
            # This is a simplified version; real logic would query DB for average
            # For now, we compare against a static threshold or a simple running average if we had one.
            # Let's assume an "Anomaly" if count jumps by > 5 in 1 second (burst) - simpler for now without DB queries in loop
            
            # Risk Logic
            crowd_risk = snapshot['risk_level'] 
            audio_status = snapshot['audio_status'] 
            
            final_risk = "SAFE"
            if audio_status == "PANIC" and crowd_risk == "HIGH":
                final_risk = "DANGER"
            elif audio_status == "PANIC" or crowd_risk == "HIGH":
                final_risk = "WARN"
            elif crowd_risk == "MEDIUM":
                final_risk = "WARN"
            else:
                final_risk = "SAFE"
            
            snapshot['risk_level'] = final_risk
            
            # Broadcast
            await self.sio.emit('state_update', snapshot)
            
            # Log to DB every 5 seconds
            if time.time() - self.last_log_time > 5:
                self.last_log_time = time.time()
                async with AsyncSessionLocal() as session:
                    log = CrowdLog(
                        person_count=snapshot['people_count'],
                        risk_score=final_risk,
                        zone_id="main",
                        coordinates=json.dumps(snapshot.get('coordinates', []))
                    )
                    session.add(log)
                    
                    # Mission V7: Persist Individual Detections
                    detections = state.get_detections_to_persist()
                    if detections:
                        for d in detections:
                            log_entry = DetectionLog(
                                x=d['x'],
                                y=d['y'],
                                map_x=d.get('map_x'),
                                map_y=d.get('map_y')
                            )
                            session.add(log_entry)
                    
                    await session.commit()
            
            # Hardware (Non-blocking)
            await asyncio.to_thread(self.arduino.send_command, f"RISK:{final_risk}")
            
            await asyncio.sleep(0.5)

hub = SentinelHub()
