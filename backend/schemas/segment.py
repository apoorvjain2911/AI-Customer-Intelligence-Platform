from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SegmentBase(BaseModel):
    customer_id: int
    segment_name: str = Field(min_length=1, max_length=64)
    cluster_label: int | None = None
    confidence_score: float | None = Field(default=None, ge=0, le=1)
    centroid_distance: float | None = Field(default=None, ge=0)
    summary: str | None = None
    status: str = Field(default="active", max_length=32)


class SegmentCreate(SegmentBase):
    created_by_id: int | None = None


class SegmentUpdate(BaseModel):
    customer_id: int | None = None
    segment_name: str | None = Field(default=None, min_length=1, max_length=64)
    cluster_label: int | None = None
    confidence_score: float | None = Field(default=None, ge=0, le=1)
    centroid_distance: float | None = Field(default=None, ge=0)
    summary: str | None = None
    status: str | None = Field(default=None, max_length=32)


class SegmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    segment_name: str
    cluster_label: int | None = None
    confidence_score: float | None = None
    centroid_distance: float | None = None
    summary: str | None = None
    status: str
    created_by_id: int | None = None
    updated_by_id: int | None = None
    created_at: datetime
    updated_at: datetime


class SegmentListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[SegmentResponse]
    total: int