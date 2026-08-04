from __future__ import annotations

from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.report import Report
from schemas.report import ReportCreate, ReportUpdate


def create_report(
    db: Session,
    report_data: ReportCreate,
) -> Report:
    report = Report(
        report_type=report_data.report_type,
        title=report_data.title,
        description=report_data.description,
        file_format=report_data.file_format,
        file_path=report_data.file_path,
        status=report_data.status,
        generated_by_id=report_data.generated_by_id,
    )

    db.add(report)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create report",
        ) from exc

    db.refresh(report)
    return report


def get_report_by_id(db: Session, report_id: int) -> Report | None:
    report = db.query(Report).filter(Report.id == report_id).first()

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    return report


def list_reports(
    db: Session,
    report_type: str | None = None,
    status_filter: str | None = None,
    file_format: str | None = None,
    generated_by_id: int | None = None,
) -> Sequence[Report]:
    query = db.query(Report)

    if report_type:
        query = query.filter(Report.report_type == report_type)

    if status_filter:
        query = query.filter(Report.status == status_filter)

    if file_format:
        query = query.filter(Report.file_format == file_format)

    if generated_by_id is not None:
        query = query.filter(Report.generated_by_id == generated_by_id)

    return query.order_by(Report.created_at.desc(), Report.id.desc()).all()


def update_report(
    db: Session,
    report_id: int,
    report_data: ReportUpdate,
) -> Report:
    report = get_report_by_id(db, report_id)

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    payload = report_data.model_dump(exclude_unset=True)

    for field_name, field_value in payload.items():
        setattr(report, field_name, field_value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to update report",
        ) from exc

    db.refresh(report)
    return report


def delete_report(db: Session, report_id: int) -> None:
    report = get_report_by_id(db, report_id)

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    db.delete(report)
    db.commit()


def count_reports(db: Session) -> int:
    return db.query(Report).count()


def list_report_types(db: Session) -> list[str]:
    rows = (
        db.query(Report.report_type)
        .distinct()
        .order_by(Report.report_type.asc())
        .all()
    )

    return [row[0] for row in rows if row[0]]