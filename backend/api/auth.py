from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.security import get_current_admin, get_current_user
from database.db import get_db
from models.user import User
from schemas.auth import (
    TokenResponse,
    UserRegister,
    UserLogin,
    UserResponse,
)
from services.auth_service import (
    register_user,
    authenticate_user,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user: UserRegister,
    db: Session = Depends(get_db),
):
    return register_user(db, user)


@router.post("/login", response_model=TokenResponse)
def login(
    user: UserLogin,
    db: Session = Depends(get_db),
):

    token = authenticate_user(
        db,
        user.email,
        user.password,
    )

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/admin-test")
def admin_test(current_admin: User = Depends(get_current_admin)):
    return {
        "message": "Admin access granted",
        "user_id": current_admin.id,
        "email": current_admin.email,
        "role": current_admin.role,
    }