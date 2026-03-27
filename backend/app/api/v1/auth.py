from datetime import datetime, timedelta, timezone
from typing import Any, Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import verify_password
from app.db.session import get_db
from app.models.assistant import Assistant
from app.models.student import Student

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode: dict[str, Any] = data.copy()
    expire = datetime.now(timezone.utc) + (
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        if not expires_delta
        else expires_delta
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


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
        email = payload.get("sub")
        role = payload.get("role")
        if email is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if not isinstance(email, str) or not isinstance(role, str):
        raise credentials_exception

    if role == "student":
        result = await db.execute(select(Student).where(Student.email == email))
        user = result.scalar_one_or_none()
    elif role == "assistant":
        result = await db.execute(select(Assistant).where(Assistant.email == email))
        user = result.scalar_one_or_none()
    else:
        raise credentials_exception

    if user is None:
        raise credentials_exception

    return UserResponse(id=user.id, name=user.name, email=user.email, role=role)


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Student).where(Student.email == form_data.username)
    )
    student = result.scalar_one_or_none()

    role = "student"
    user = student

    if not student:
        result = await db.execute(
            select(Assistant).where(Assistant.email == form_data.username)
        )
        assistant = result.scalar_one_or_none()
        if assistant:
            user = assistant
            role = "assistant"

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email, "role": role})

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(id=user.id, name=user.name, email=user.email, role=role),
    )


@router.post("/logout")
async def logout(current_user: UserResponse = Depends(get_current_user)):
    return {"message": "Successfully logged out"}
