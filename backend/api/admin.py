from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.security import get_current_admin
from database.db import get_db
from models.user import User
from schemas.admin import (
    AdminDashboardResponse,
    AdminSetActiveRequest,
    AdminUpdateRoleRequest,
    AdminUserResponse,
    ModelStatusResponse,
    RetrainResponse,
)
from services.admin_service import (
    get_admin_dashboard_state,
    get_model_status,
    list_users,
    retrain_model_from_latest_upload,
    set_user_active_status,
    update_user_role,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[AdminUserResponse])
def admin_list_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return list_users(db)


@router.patch("/users/{user_id}/role", response_model=AdminUserResponse)
def admin_update_role(
    user_id: int,
    payload: AdminUpdateRoleRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return update_user_role(db, user_id, payload.role)


@router.patch("/users/{user_id}/status", response_model=AdminUserResponse)
def admin_update_status(
    user_id: int,
    payload: AdminSetActiveRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return set_user_active_status(db, user_id, payload.is_active)


@router.get("/model-status", response_model=ModelStatusResponse)
def admin_model_status(
    _: User = Depends(get_current_admin),
):
    return get_model_status()


@router.post("/retrain", response_model=RetrainResponse)
def admin_retrain_model(
    _: User = Depends(get_current_admin),
):
    return retrain_model_from_latest_upload()


@router.get("/dashboard", response_model=AdminDashboardResponse)
def admin_dashboard(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return get_admin_dashboard_state(db)