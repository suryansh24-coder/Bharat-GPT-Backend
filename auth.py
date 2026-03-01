from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_limiter.depends import RateLimiter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, User, Token
from app.auth.jwt import get_password_hash, verify_password, create_access_token
from app.config import settings

router = APIRouter()

@router.post("/register", response_model=User)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check existing user
    result = await db.execute(select(UserModel).where(UserModel.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    user = UserModel(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login", response_model=Token, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def login_access_token(
    request: Request,
    db: AsyncSession = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    result = await db.execute(select(UserModel).where(UserModel.email == form_data.username))
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
