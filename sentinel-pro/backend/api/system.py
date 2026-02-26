import cv2
import numpy as np
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel
from typing import List

from backend.api.deps import get_db
from backend.db.models import SystemConfig, Calibration
from backend.core.sentinel_hub import hub

router = APIRouter()

class Point(BaseModel):
    x: float
    y: float

class CalibrationRequest(BaseModel):
    name: str = "Last Calibration"
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

@router.post("/calibrations")
async def save_named_calibration(data: CalibrationRequest, db: AsyncSession = Depends(get_db)):
    """Save a named calibration to the library"""
    if len(data.camera_points) != 4 or len(data.map_points) != 4:
        raise HTTPException(status_code=400, detail="Exactly 4 points required")

    src_pts = np.float32([[p.x, p.y] for p in data.camera_points])
    dst_pts = np.float32([[p.x, p.y] for p in data.map_points])
    H, _ = cv2.findHomography(src_pts, dst_pts)
    
    if H is None:
        raise HTTPException(status_code=500, detail="Homography failed")

    matrix_json = json.dumps(H.tolist())
    points_json = json.dumps({
        "camera": [p.dict() for p in data.camera_points],
        "map": [p.dict() for p in data.map_points]
    })

    # Save to Calibration table
    result = await db.execute(select(Calibration).where(Calibration.name == data.name))
    cal = result.scalar_one_or_none()
    
    if cal:
        cal.matrix = matrix_json
        cal.points = points_json
        cal.is_active = True
    else:
        cal = Calibration(
            name=data.name,
            matrix=matrix_json,
            points=points_json,
            is_active=True
        )
        db.add(cal)
    
    # Deactivate others if this is active
    await db.execute(text("UPDATE calibrations SET is_active = FALSE WHERE name != :name"), {"name": data.name})
    await db.commit()
    
    hub.update_homography_matrix(H.tolist())
    return {"id": cal.id, "name": cal.name, "status": "saved"}

@router.get("/calibrations")
async def list_calibrations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Calibration))
    return result.scalars().all()

@router.post("/calibrations/{id}/activate")
async def activate_calibration(id: int, db: AsyncSession = Depends(get_db)):
    # Deactivate all
    await db.execute(text("UPDATE calibrations SET is_active = FALSE"))
    
    result = await db.execute(select(Calibration).where(Calibration.id == id))
    cal = result.scalar_one_or_none()
    if not cal:
        raise HTTPException(status_code=404, detail="Calibration not found")
    
    cal.is_active = True
    await db.commit()
    
    # Mission V8: Broadcast activation to swap Dashboard backgrounds
    await hub.sio.emit('config_activated', {
        'id': cal.id,
        'name': cal.name,
        'points': json.loads(cal.points)
    })
    
    hub.update_homography_matrix(json.loads(cal.matrix))
    return {"status": "activated", "name": cal.name}

@router.delete("/calibrations/{id}")
async def delete_calibration(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Calibration).where(Calibration.id == id))
    cal = result.scalar_one_or_none()
    if cal:
        await db.delete(cal)
        await db.commit()
    return {"status": "deleted"}
