import cv2
import numpy as np
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List

from backend.api.deps import get_db
from backend.db.models import SystemConfig
from backend.core.sentinel_hub import hub

router = APIRouter()

class Point(BaseModel):
    x: float
    y: float

class CalibrationRequest(BaseModel):
    camera_points: List[Point] # Points on video feed
    map_points: List[Point]    # Points on floor plan

@router.post("/calibrate")
async def calibrate_camera(data: CalibrationRequest, db: AsyncSession = Depends(get_db)):
    if len(data.camera_points) != 4 or len(data.map_points) != 4:
        raise HTTPException(status_code=400, detail="Exactly 4 points required for both camera and map")

    # Convert to numpy arrays
    src_pts = np.float32([[p.x, p.y] for p in data.camera_points]) # Camera
    dst_pts = np.float32([[p.x, p.y] for p in data.map_points])    # Map

    # Compute Homography
    H, status = cv2.findHomography(src_pts, dst_pts)
    
    if H is None:
        raise HTTPException(status_code=500, detail="Homography calculation failed")

    # Serialize to JSON list for storage
    h_list = H.tolist()
    h_json = json.dumps(h_list)

    # Save to DB - key="homography_matrix"
    result = await db.execute(select(SystemConfig).where(SystemConfig.key == "homography_matrix"))
    config_entry = result.scalar_one_or_none()

    if config_entry:
        config_entry.value = h_json
    else:
        config_entry = SystemConfig(key="homography_matrix", value=h_json, description="3x3 Homography Matrix")
        db.add(config_entry)
    
    await db.commit()

    # Update Runtime Engine
    hub.update_homography_matrix(h_list)

    return {"status": "success", "message": "Calibration saved and applied", "matrix": h_list}

@router.get("/config")
async def get_config(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SystemConfig))
    configs = result.scalars().all()
    return {c.key: c.value for c in configs}
