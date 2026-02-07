import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.config import DATABASE_URL
from backend.db.models import User

async def check_user():
    print(f"Connecting to DB at: {DATABASE_URL}")
    try:
        engine = create_async_engine(DATABASE_URL)
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    except Exception as e:
        print(f"FAILED to Create Engine: {e}")
        return

    try:
        async with async_session() as session:
            print("Session created. Querying for 'admin' user...")
            result = await session.execute(select(User).where(User.username == "admin"))
            user = result.scalars().first()
            
            if user:
                print(f"SUCCESS: User '{user.username}' found (ID: {user.id}).")
                print("Database connection is GOOD.")
            else:
                print("FAILURE: User 'admin' NOT FOUND.")
                print("Database connection seems OK, but seeding is required.")
                
    except Exception as e:
        print(f"FAILED to Query Database: {e}")
        print("Check if PostgreSQL is running and credentials are correct.")
    
    await engine.dispose()

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(check_user())
    except Exception as e:
        print(f"Error running check: {e}")
