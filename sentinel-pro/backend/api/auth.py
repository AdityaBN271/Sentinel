from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.api.schemas import LoginRequest, LoginResponse
from backend.db.models import User
from backend.core.security import verify_password, create_access_token
from backend.api.deps import get_db

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(creds: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Authenticate User
    result = await db.execute(select(User).where(User.username == creds.username))
    user = result.scalars().first()

    if not user or not verify_password(creds.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate Token
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "message": "Login successful",
        "token": access_token
    }
