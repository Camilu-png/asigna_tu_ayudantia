from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from app.core.security import verify_password
from app.db.session import get_db
from app.models.user import User
from app.models.user_course import UserCourse

router = APIRouter(prefix="/auth", tags=["auth"])

limiter = Limiter(key_func=get_remote_address)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode: dict[str, Any] = data.copy()
    expire = datetime.now(timezone.utc) + (
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        if not expires_delta
        else expires_delta
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode: dict[str, Any] = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_user_role(db: AsyncSession, user_id: int) -> str:
    result = await db.execute(select(UserCourse).where(UserCourse.user_id == user_id))
    user_courses = result.scalars().all()
    roles = set(uc.role for uc in user_courses)
    if "ASSISTANT" in roles:
        return "assistant"
    if "STUDENT" in roles:
        return "student"
    return "user"


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload: dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get("type")
        if token_type != "access":
            raise credentials_exception
        email = payload.get("sub")
        role = payload.get("role")
        if email is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if not isinstance(email, str) or not isinstance(role, str):
        raise credentials_exception

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return UserResponse(id=user.id, name=user.name, email=user.email, role=role)


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role = await get_user_role(db, user.id)

    access_token = create_access_token(data={"sub": user.email, "role": role})
    refresh_token = create_refresh_token(data={"sub": user.email, "role": role})

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse(id=user.id, name=user.name, email=user.email, role=role),
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: dict):
    refresh_token = token_data.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="refresh_token is required",
        )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload: dict[str, Any] = jwt.decode(
            refresh_token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_type = payload.get("type")
        if token_type != "refresh":
            raise credentials_exception
        email = payload.get("sub")
        role = payload.get("role")
        if email is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if not isinstance(email, str) or not isinstance(role, str):
        raise credentials_exception

    access_token = create_access_token(data={"sub": email, "role": role})
    new_refresh_token = create_refresh_token(data={"sub": email, "role": role})

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


@router.post("/logout")
async def logout(current_user: UserResponse = Depends(get_current_user)):
    return {"message": "Successfully logged out"}
