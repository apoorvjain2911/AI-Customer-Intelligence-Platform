from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.db import get_db
from models.user import User
from schemas.report import (
    ReportCreate,
    ReportListResponse,
    ReportResponse,
    ReportUpdate,
)
from services.report_service import (
    create_report,
    delete_report,
    get_report_by_id,
    list_reports,
    update_report,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report_endpoint(
    report: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payload = report.model_copy(update={"generated_by_id": current_user.id})
    return create_report(db, payload)


@router.get("", response_model=ReportListResponse)
def list_reports_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    report_type: str | None = Query(default=None, max_length=64),
    status_filter: str | None = Query(default=None, alias="status", max_length=32),
    file_format: str | None = Query(default=None, max_length=16),
):
    records = list_reports(
        db,
        report_type=report_type,
        status_filter=status_filter,
        file_format=file_format,
        generated_by_id=current_user.id,
    )
    return {"items": records, "total": len(records)}


@router.get("/{report_id}", response_model=ReportResponse)
def get_report_endpoint(
    report_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_report_by_id(db, report_id)


@router.put("/{report_id}", response_model=ReportResponse)
def update_report_endpoint(
    report_id: int,
    report: ReportUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return update_report(db, report_id, report)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report_endpoint(
    report_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    delete_report(db, report_id)
    return None