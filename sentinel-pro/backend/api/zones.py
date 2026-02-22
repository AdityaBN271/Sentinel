from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from typing import List
import json

from backend.api.deps import get_db
from backend.db.models import Zone

router = APIRouter()

class ZoneCreate(BaseModel):
    name: str
    polygon_data: List[List[float]] # [[x,y], [x,y]...]
    capacity: int = 50
    alert_threshold: int = 80

class ZoneResponse(BaseModel):
    id: int
    name: str
    polygon_data: str
    capacity: int
    alert_threshold: int

    class Config:
        from_attributes = True

@router.post("/", response_model=ZoneResponse)
async def create_zone(data: ZoneCreate, db: AsyncSession = Depends(get_db)):
    # Check if exists
    result = await db.execute(select(Zone).where(Zone.name == data.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Zone name already exists")
    
    zone = Zone(
        name=data.name,
        polygon_data=json.dumps(data.polygon_data),
        capacity=data.capacity,
        alert_threshold=data.alert_threshold
    )
    db.add(zone)
    await db.commit()
    await db.refresh(zone)
    return zone

@router.get("/", response_model=List[ZoneResponse])
async def list_zones(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Zone))
    return result.scalars().all()

@router.delete("/{zone_id}")
async def delete_zone(zone_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Zone).where(Zone.id == zone_id))
    await db.commit()
    return {"status": "success"}
