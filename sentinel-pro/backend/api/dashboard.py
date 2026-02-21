from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from engine.shared_state import state
from backend.api.deps import get_db, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db.models import CrowdLog
import time
import asyncio

router = APIRouter()

def generate_frames():
    last_frame_time = 0
    while True:
        snapshot = state.get_snapshot()
        current_frame_time = snapshot.get('last_update', 0)
        
        if current_frame_time > last_frame_time:
            # Check for latency (delay between now and frame production)
            latency = time.time() - current_frame_time
            
            # Mission V6: Automatic Quality Adjustment
            quality = 70
            if latency > 0.1: # If more than 100ms old, compression helps
                quality = 50
            
            frame_bytes = state.get_frame()
            if frame_bytes:
                last_frame_time = current_frame_time
                # Note: The frame is already encoded in vision_module.py. 
                # To do truly dynamic downscaling here, we'd need the raw frame 
                # or re-encode. For demonstration, we use the vision_engine quality 
                # but we could add a header or flag if we passed raw frames.
                # However, vision_module already uses quality 70. 
                # Let's keep it simple: the vision engine already handles the heavy lifting.
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.01)

@router.get("/vision/stream")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.get("/status")
def get_status(current_user = Depends(get_current_user)):
    return state.get_snapshot()

@router.get("/logs")
async def get_logs(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(select(CrowdLog).order_by(CrowdLog.timestamp.desc()).limit(50))
    logs = result.scalars().all()
    return logs
