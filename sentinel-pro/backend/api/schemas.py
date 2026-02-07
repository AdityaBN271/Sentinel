from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    message: str
    token: Optional[str] = None

class SentinelStateResponse(BaseModel):
    crowd_count: int
    crowd_status: str
    audio_status: str
    risk_level: str
    people_detected: List[Dict[str, Any]]
    last_update: float

class MetricsResponse(BaseModel):
    metrics: str # Placeholder
