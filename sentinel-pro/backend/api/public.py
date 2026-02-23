from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime

from backend.api.deps import get_db
from backend.db.models import Zone, SystemConfig, Incident
from engine.shared_state import state

router = APIRouter()

@router.get("/mobile-sync")
async def get_mobile_sync_data(db: AsyncSession = Depends(get_db)):
    """Comprehensive sync for mobile attendee app"""
    # 1. Get Live Zone Counts from SharedState (V11 PIP implementation)
    zone_counts = state.metrics.get('zone_counts', {})
    
    # 2. Get Zone metadata from DB
    result = await db.execute(select(Zone))
    zones = result.scalars().all()
    
    zone_data = []
    for z in zones:
        occupancy = zone_counts.get(z.name, 0)
        density_pct = (occupancy / max(1, z.capacity)) * 100
        
        status = "GREEN"
        if density_pct > z.alert_threshold:
            status = "RED"
        elif density_pct > 50:
            status = "YELLOW"
            
        zone_data.append({
            "name": z.name,
            "occupancy": occupancy,
            "capacity": z.capacity,
            "density_percentage": round(density_pct, 1),
            "status": status
        })

    # 3. Get any active admin alerts (mocked for now, can be system_config)
    admin_alert = "All systems clear. Stay safe."
    
    return {
        "floor_plan_url": "/floor_plan.png",
        "risk_level": state.metrics.get('risk_level', 'NORMAL'),
        "admin_alert": admin_alert,
        "zones": zone_data,
        "timestamp": datetime.now().isoformat()
    }

class SOSPayload(BaseModel):
    session_id: str
    details: str = "Emergency SOS Triggered"

@router.post("/sos")
async def trigger_sos(data: SOSPayload, db: AsyncSession = Depends(get_db)):
    """Handle SOS trigger from mobile app"""
    incident = Incident(
        session_id=data.session_id,
        alert_type="SOS",
        details=data.details,
        acknowledged=False,
        is_resolved=False
    )
    db.add(incident)
    await db.commit()
    return {"status": "success", "message": "SOS alert received. Assistance is on the way."}

@router.get("/safety")
async def get_public_safety_data(db: AsyncSession = Depends(get_db)):
    # Existing method kept for compatibility, using the same logic as mobile-sync
    return await get_mobile_sync_data(db)
