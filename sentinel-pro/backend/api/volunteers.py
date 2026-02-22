from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
import requests
import json

from backend.api.deps import get_db
from backend.db.models import Volunteer
import backend.core.config as config

router = APIRouter()

# SMS API key is now managed in backend/core/config.py

class VolunteerCreate(BaseModel):
    name: str
    phone: str
    role: str = "Marshall"
    assigned_zone: Optional[str] = None

class VolunteerResponse(BaseModel):
    id: int
    name: str
    phone: str
    role: str
    assigned_zone: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

def send_assignment_sms(name: str, zone: str, phone: str):
    """Trigger Fast2SMS API to send assignment alert"""
    key = config.FAST2SMS_API_KEY
    if not key or key == "YOUR_FAST2SMS_API_KEY":
        print(f"[SMS MOCK] Sentinel-Pro: {name}, report to {zone} immediately.")
        return False

    # Clean phone number (Fast2SMS expects 10 digits for Indian numbers)
    # Remove any non-numeric chars like +, spaces, etc.
    clean_phone = "".join(filter(str.isdigit, phone))
    if len(clean_phone) > 10 and clean_phone.startswith("91"):
        clean_phone = clean_phone[-10:] # Use last 10 digits

    url = "https://www.fast2sms.com/dev/bulkV2"
    payload = {
        "message": f"Sentinel-Pro: {name}, report to {zone} for duty immediately.",
        "language": "english",
        "route": "v3", # v3 is more reliable for bulkV2 text messages
        "numbers": clean_phone
    }
    headers = {
        "authorization": key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        res_json = response.json()
        print(f"[SMS DEBUG] Sending to {clean_phone} via v3. Status: {response.status_code}")
        print(f"[SMS DEBUG] Response JSON: {res_json}")
        return res_json.get("return", False)
    except Exception as e:
        print(f"[SMS ERROR] {e}")
        return False

@router.post("/", response_model=VolunteerResponse)
async def create_volunteer(data: VolunteerCreate, db: AsyncSession = Depends(get_db)):
    vol = Volunteer(**data.dict())
    db.add(vol)
    await db.commit()
    await db.refresh(vol)
    
    # If assigned to a zone, send SMS
    if vol.assigned_zone:
        send_assignment_sms(vol.name, vol.assigned_zone, vol.phone)
        
    return vol

@router.get("/", response_model=List[VolunteerResponse])
async def list_volunteers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Volunteer).where(Volunteer.is_active == True))
    return result.scalars().all()

@router.delete("/{vol_id}")
async def delete_volunteer(vol_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Volunteer).where(Volunteer.id == vol_id))
    vol = result.scalar_one_or_none()
    if not vol:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    
    vol.is_active = False # Soft delete
    await db.commit()
    return {"status": "success", "message": "Volunteer removed"}

@router.post("/{vol_id}/assign")
async def assign_zone(vol_id: int, zone_name: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Volunteer).where(Volunteer.id == vol_id))
    vol = result.scalar_one_or_none()
    if not vol:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    
    vol.assigned_zone = zone_name
    await db.commit()
    
    # Send SMS alert
    status = send_assignment_sms(vol.name, zone_name, vol.phone)
    
    return {"status": "success", "sms_sent": status}
