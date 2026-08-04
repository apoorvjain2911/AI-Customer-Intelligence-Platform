from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AdminUpdateRoleRequest(BaseModel):
    role: str = Field(min_length=1, max_length=64)


class AdminSetActiveRequest(BaseModel):
    is_active: bool


class ModelStatusResponse(BaseModel):
    model_exists: bool
    pipeline_exists: bool
    model_path: str
    pipeline_path: str
    model_modified_at: str | None = None
    pipeline_modified_at: str | None = None
    model_size_bytes: int
    pipeline_size_bytes: int
    latest_upload_exists: bool
    latest_upload_modified_at: str | None = None


class TrainingFeatureImportance(BaseModel):
    feature: str
    importance: float


class TrainingResultResponse(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    feature_importance: list[TrainingFeatureImportance]


class RetrainResponse(BaseModel):
    message: str
    model_status: ModelStatusResponse
    training_result: TrainingResultResponse


class AdminDashboardResponse(BaseModel):
    user_metrics: dict[str, Any]
    model_status: ModelStatusResponse
    recent_users: list[AdminUserResponse]
    activity_logs: list[dict[str, Any]]