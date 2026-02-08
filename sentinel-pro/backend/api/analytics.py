from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from backend.db.models import CrowdLog
from backend.api.deps import get_db
import datetime

router = APIRouter()

@router.get("/peak-hour")
async def get_peak_hour(db: AsyncSession = Depends(get_db)):
    """
    Get the hour of the day with the highest average person count.
    This is a simplified analytics query.
    """
    # Since sqlite/asyncpg differences can make date truncation complex in raw sql across different DBs,
    # we'll fetch recent logs and process in python for this MVP or use a simple aggregation.
    
    # Fetch logs from last 24 hours
    one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    result = await db.execute(
        select(CrowdLog).where(CrowdLog.timestamp >= one_day_ago)
    )
    logs = result.scalars().all()
    
    if not logs:
        return {"peak_hour": None, "max_count": 0}

    # Aggregate by hour
    hour_counts = {}
    for log in logs:
        # Assuming timestamp is datetime object
        hour = log.timestamp.hour
        hour_counts[hour] = hour_counts.get(hour, []) + [log.person_count]
        
    # Calculate average per hour
    peak_hour = -1
    max_avg = -1
    
    hourly_data = []
    
    for hour, counts in hour_counts.items():
        avg = sum(counts) / len(counts)
        hourly_data.append({"hour": hour, "count": avg})
        if avg > max_avg:
            max_avg = avg
            peak_hour = hour
            
    return {
        "peak_hour": peak_hour,
        "max_average_count": max_avg,
        "hourly_data": sorted(hourly_data, key=lambda x: x['hour'])
    }

@router.get("/history")
async def get_history(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Fetch recent logs for chart"""
    result = await db.execute(
        select(CrowdLog).order_by(desc(CrowdLog.timestamp)).limit(limit)
    )
    logs = result.scalars().all()
    return logs
