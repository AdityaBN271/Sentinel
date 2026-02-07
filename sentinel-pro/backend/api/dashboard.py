from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from engine.shared_state import state
from backend.api.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db.models import CrowdLog
import time
import asyncio

router = APIRouter()

def generate_frames():
    while True:
        frame_bytes = state.get_frame()
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.04) # ~25 FPS

@router.get("/vision/stream")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.get("/status")
def get_status():
    return state.get_snapshot()

@router.get("/logs")
async def get_logs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CrowdLog).order_by(CrowdLog.timestamp.desc()).limit(50))
    logs = result.scalars().all()
    return logs
