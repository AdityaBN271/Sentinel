import socketio
import asyncio
import time
from engine.shared_state import state
from .serial_bridge import ArduinoBridge
from backend.api.deps import AsyncSessionLocal
from backend.db.models import CrowdLog

class SentinelHub:
    def __init__(self):
        self.sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
        self.app = socketio.ASGIApp(self.sio)
        self.arduino = ArduinoBridge()
        self.last_log_time = time.time()

    async def monitor_loop(self):
        print("[Hub] Monitor Loop Started")
        while True:
            snapshot = state.get_snapshot()
            
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
                        zone_id="main"
                    )
                    session.add(log)
                    await session.commit()
            
            # Hardware (Non-blocking)
            await asyncio.to_thread(self.arduino.send_command, f"RISK:{final_risk}")
            
            await asyncio.sleep(0.5)

hub = SentinelHub()
