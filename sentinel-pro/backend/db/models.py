from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="operator") # admin, operator
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CrowdLog(Base):
    """High frequency logs from AI engine"""
    __tablename__ = "crowd_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    person_count = Column(Integer, default=0)
    risk_score = Column(String, default="LOW")
    zone_id = Column(String, default="default")
    coordinates = Column(String, nullable=True) # JSON string of coordinates

    incidents = relationship("Incident", back_populates="crowd_log")

class Incident(Base):
    """Critical alerts (Level 1)"""
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    crowd_log_id = Column(Integer, ForeignKey("crowd_logs.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    alert_type = Column(String) # PANIC_AUDIO, HIGH_DENSITY, COMPOSITE
    details = Column(String)
    acknowledged = Column(Boolean, default=False)

    crowd_log = relationship("CrowdLog", back_populates="incidents")

class SystemConfig(Base):
    """Dynamic configuration values"""
    __tablename__ = "system_config"

    key = Column(String, primary_key=True, index=True)
    value = Column(String) # Store as string, cast when reading
    description = Column(String, nullable=True)
