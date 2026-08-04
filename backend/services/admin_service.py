from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from database.db import SessionLocal
from models.user import User
from services.preprocess import LATEST_UPLOAD_PATH, MODEL_PATH, PIPELINE_PATH, ensure_storage_directories, read_csv
from services.trainer import TrainingResult, load_latest_uploaded_dataframe, train_model_from_frame


VALID_ROLES = {"admin", "sales_manager", "customer_success_manager"}


def _safe_timestamp(path: Path) -> str | None:
    if not path.exists():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def _serialize_user(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


def list_users(
    db: Session,
    *,
    role: str | None = None,
    is_active: bool | None = None,
) -> list[dict[str, Any]]:
    query = db.query(User)

    if role:
        query = query.filter(User.role == role)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    return [_serialize_user(user) for user in query.order_by(User.created_at.desc(), User.id.desc()).all()]


def get_user_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def update_user_role(db: Session, user_id: int, role: str) -> dict[str, Any]:
    normalized_role = role.strip().lower()
    if normalized_role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Allowed roles: {', '.join(sorted(VALID_ROLES))}",
        )

    user = get_user_by_id(db, user_id)
    user.role = normalized_role
    db.commit()
    db.refresh(user)
    return _serialize_user(user)


def set_user_active_status(db: Session, user_id: int, is_active: bool) -> dict[str, Any]:
    user = get_user_by_id(db, user_id)
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return _serialize_user(user)


def get_model_status() -> dict[str, Any]:
    ensure_storage_directories()

    model_exists = MODEL_PATH.exists()
    pipeline_exists = PIPELINE_PATH.exists()

    return {
        "model_exists": model_exists,
        "pipeline_exists": pipeline_exists,
        "model_path": str(MODEL_PATH),
        "pipeline_path": str(PIPELINE_PATH),
        "model_modified_at": _safe_timestamp(MODEL_PATH),
        "pipeline_modified_at": _safe_timestamp(PIPELINE_PATH),
        "model_size_bytes": MODEL_PATH.stat().st_size if model_exists else 0,
        "pipeline_size_bytes": PIPELINE_PATH.stat().st_size if pipeline_exists else 0,
        "latest_upload_exists": LATEST_UPLOAD_PATH.exists(),
        "latest_upload_modified_at": _safe_timestamp(LATEST_UPLOAD_PATH),
    }


def retrain_model_from_latest_upload() -> dict[str, Any]:
    dataset = load_latest_uploaded_dataframe()
    training_result: TrainingResult = train_model_from_frame(dataset)

    return {
        "message": "Model retrained successfully",
        "model_status": get_model_status(),
        "training_result": training_result.to_dict(),
    }


def retrain_model_from_path(file_path: str | Path) -> dict[str, Any]:
    if str(file_path).strip() == "latest":
        dataset = load_latest_uploaded_dataframe()
    else:
        dataset = read_csv(file_path)

    training_result = train_model_from_frame(dataset)
    return {
        "message": "Model retrained successfully",
        "model_status": get_model_status(),
        "training_result": training_result.to_dict(),
    }


def get_admin_dashboard_state(db: Session) -> dict[str, Any]:
    users = db.query(User).all()
    role_counts: dict[str, int] = {}
    for user in users:
        role_counts[user.role] = role_counts.get(user.role, 0) + 1

    return {
        "user_metrics": {
            "total_users": len(users),
            "active_users": sum(1 for user in users if user.is_active),
            "inactive_users": sum(1 for user in users if not user.is_active),
            "role_distribution": [
                {"name": role, "value": count}
                for role, count in sorted(role_counts.items())
            ],
        },
        "model_status": get_model_status(),
        "recent_users": [_serialize_user(user) for user in users[:10]],
        "activity_logs": [],
    }


def open_admin_session() -> Session:
    return SessionLocal()