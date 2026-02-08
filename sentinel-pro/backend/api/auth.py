from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.api.schemas import LoginRequest, LoginResponse
from backend.db.models import User
from backend.core.security import verify_password, create_access_token, get_password_hash
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

@router.post("/register", response_model=LoginResponse)
async def register(creds: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.username == creds.username))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Create new user
    hashed_pw = get_password_hash(creds.password)
    new_user = User(username=creds.username, hashed_password=hashed_pw)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Generate Token
    access_token = create_access_token(data={"sub": new_user.username})
    
    return {
        "message": "Registration successful",
        "token": access_token
    }
