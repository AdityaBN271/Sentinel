import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.db.models import User
from backend.core.security import get_password_hash
from backend.core.config import DATABASE_URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

async def create_admin():
    print(f"Connecting to database...")
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session() as session:
        # Check if admin exists
        result = await session.execute(select(User).where(User.username == "admin"))
        existing_admin = result.scalars().first()

        if existing_admin:
            print("Admin user already exists.")
        else:
            print("Creating admin user...")
            admin_user = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                is_active=True
            )
            session.add(admin_user)
            await session.commit()
            print("Admin user created successfully (username: admin, password: admin123).")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_admin())
