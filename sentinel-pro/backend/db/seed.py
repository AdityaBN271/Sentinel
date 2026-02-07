import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.core.config import DATABASE_URL
from backend.db.models import Base, User, CrowdLog, SystemConfig

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session() as session:
        async with session.begin():
            # 1. Create Admin
            admin_user = User(
                username="admin", 
                hashed_password=pwd_context.hash("admin123"), 
                role="admin"
            )
            session.add(admin_user)
            print("Added User: admin")

            # 2. Create Configs
            configs = [
                SystemConfig(key="yolo_conf", value="0.25", description="Confidence Threshold"),
                SystemConfig(key="audio_sens", value="0.05", description="RMS Audio Threshold"),
            ]
            session.add_all(configs)
            print(f"Added {len(configs)} Configs")

            # 3. Create Mock Logs
            logs = []
            for i in range(10):
                log = CrowdLog(
                    person_count=i*2,
                    risk_score="LOW" if i < 5 else "MEDIUM",
                    zone_id="Gate_A"
                )
                logs.append(log)
            session.add_all(logs)
            print("Added 10 Mock CrowdLogs")
    
    await engine.dispose()
    print("Seeding Complete!")

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(seed())
    except Exception as e:
        print(f"Error: {e}")
