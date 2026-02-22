from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import json

from backend.api.deps import get_db
from backend.db.models import Zone, SystemConfig
from engine.shared_state import state

router = APIRouter()

@router.get("/safety")
async def get_public_safety_data(db: AsyncSession = Depends(get_db)):
    """Read-only safety data for mobile app"""
    # 1. Get Zones
    result = await db.execute(select(Zone))
    zones = result.scalars().all()
    
    # 2. Map Density (Mocking live calc for density based on state.metrics)
    # In a real app, we'd use the PIP logic to count points per zone in the last update
    current_count = state.metrics.get('people_count', 0)
    
    zone_data = []
    for z in zones:
        # Simple proportional mock for now - in production, PIP logic would populate this
        zone_occupancy = int(current_count / max(1, len(zones))) 
        density_pct = (zone_occupancy / z.capacity) * 100
        
        status = "GREEN"
        if density_pct > z.alert_threshold:
            status = "RED"
        elif density_pct > 50:
            status = "YELLOW"
            
        zone_data.append({
            "name": z.name,
            "occupancy": zone_occupancy,
            "capacity": z.capacity,
            "density_percentage": round(density_pct, 1),
            "status": status
        })

    return {
        "floor_plan_url": "/floor_plan.png",
        "system_status": state.metrics.get('risk_level', 'NORMAL'),
        "zones": zone_data,
        "last_update": state.metrics.get('timestamp')
    }
