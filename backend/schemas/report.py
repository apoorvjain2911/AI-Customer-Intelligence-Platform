from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReportBase(BaseModel):
    report_type: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None)
    file_format: str = Field(min_length=1, max_length=16)
    file_path: str | None = Field(default=None, max_length=512)
    status: str = Field(default="generated", max_length=32)


class ReportCreate(ReportBase):
    generated_by_id: int | None = None


class ReportUpdate(BaseModel):
    report_type: str | None = Field(default=None, min_length=1, max_length=64)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    file_format: str | None = Field(default=None, min_length=1, max_length=16)
    file_path: str | None = Field(default=None, max_length=512)
    status: str | None = Field(default=None, max_length=32)


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    report_type: str
    title: str
    description: str | None = None
    file_format: str
    file_path: str | None = None
    status: str
    generated_by_id: int | None = None
    created_at: datetime
    updated_at: datetime


class ReportListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[ReportResponse]
    total: int