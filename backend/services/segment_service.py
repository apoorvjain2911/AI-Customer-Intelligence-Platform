from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.customer import Customer
from models.segment import Segment
from schemas.segment import SegmentCreate, SegmentUpdate


def _safe_float(value: object | None) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _derive_segment_name(customer: Customer) -> tuple[str, int | None, float, float, str]:
    churn_probability = _safe_float(customer.churn_probability)
    tenure = customer.tenure or 0
    monthly_charges = _safe_float(customer.monthly_charges)
    last_login = customer.last_login
    days_since_login = None

    if last_login is not None:
        now = datetime.now(timezone.utc)
        aware_last_login = last_login
        if aware_last_login.tzinfo is None:
            aware_last_login = aware_last_login.replace(tzinfo=timezone.utc)
        days_since_login = (now - aware_last_login).days

    if days_since_login is not None and days_since_login >= 90:
        return (
            "Dormant",
            None,
            max(0.0, 1 - churn_probability),
            float(days_since_login),
            "Customer has been inactive for an extended period.",
        )

    if churn_probability >= 0.75 or (customer.risk_level or "").lower() == "high":
        return (
            "At Risk",
            3,
            churn_probability,
            max(0.0, 100.0 - churn_probability * 100.0),
            "Customer shows elevated churn risk and should be prioritized.",
        )

    if tenure <= 3:
        return (
            "New",
            1,
            max(0.5, 1 - churn_probability),
            float(max(0, 3 - tenure)),
            "Customer is in the early lifecycle stage.",
        )

    if tenure >= 24 and churn_probability <= 0.35:
        return (
            "Loyal",
            2,
            max(0.6, 1 - churn_probability),
            float(max(0, 100 - tenure)),
            "Customer has strong tenure and low churn propensity.",
        )

    if monthly_charges >= 80 and churn_probability <= 0.45:
        return (
            "Premium",
            4,
            max(0.55, 1 - churn_probability),
            max(0.0, 120.0 - monthly_charges),
            "Customer contributes strong recurring revenue.",
        )

    return (
        "Stable",
        0,
        max(0.4, 1 - churn_probability),
        float(max(0, 50 - tenure)),
        "Customer is healthy but not in a premium or loyalty tier.",
    )


def create_segment(
    db: Session,
    segment_data: SegmentCreate,
    *,
    updated_by_id: int | None = None,
) -> Segment:
    customer = db.query(Customer).filter(Customer.id == segment_data.customer_id).first()

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    segment = Segment(
        customer_id=segment_data.customer_id,
        segment_name=segment_data.segment_name,
        cluster_label=segment_data.cluster_label,
        confidence_score=segment_data.confidence_score,
        centroid_distance=segment_data.centroid_distance,
        summary=segment_data.summary,
        status=segment_data.status,
        created_by_id=segment_data.created_by_id,
        updated_by_id=updated_by_id or segment_data.created_by_id,
    )

    db.add(segment)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create segment",
        ) from exc

    db.refresh(segment)
    return segment


def assign_segment_for_customer(
    db: Session,
    customer_id: int,
    *,
    created_by_id: int | None = None,
) -> Segment:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    segment_name, cluster_label, confidence_score, centroid_distance, summary = _derive_segment_name(customer)

    existing_segment = (
        db.query(Segment)
        .filter(Segment.customer_id == customer_id)
        .order_by(Segment.created_at.desc(), Segment.id.desc())
        .first()
    )

    if existing_segment is None:
        return create_segment(
            db,
            SegmentCreate(
                customer_id=customer_id,
                segment_name=segment_name,
                cluster_label=cluster_label,
                confidence_score=min(max(confidence_score, 0.0), 1.0),
                centroid_distance=max(0.0, centroid_distance),
                summary=summary,
                status="active",
                created_by_id=created_by_id,
            ),
            updated_by_id=created_by_id,
        )

    existing_segment.segment_name = segment_name
    existing_segment.cluster_label = cluster_label
    existing_segment.confidence_score = min(max(confidence_score, 0.0), 1.0)
    existing_segment.centroid_distance = max(0.0, centroid_distance)
    existing_segment.summary = summary
    existing_segment.status = "active"
    existing_segment.updated_by_id = created_by_id

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to update segment",
        ) from exc

    db.refresh(existing_segment)
    return existing_segment


def get_segment_by_id(db: Session, segment_id: int) -> Segment | None:
    segment = db.query(Segment).filter(Segment.id == segment_id).first()

    if segment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Segment not found",
        )

    return segment


def list_segments(
    db: Session,
    *,
    customer_id: int | None = None,
    segment_name: str | None = None,
    status_filter: str | None = None,
) -> Sequence[Segment]:
    query = db.query(Segment)

    if customer_id is not None:
        query = query.filter(Segment.customer_id == customer_id)

    if segment_name:
        query = query.filter(Segment.segment_name == segment_name)

    if status_filter:
        query = query.filter(Segment.status == status_filter)

    return query.order_by(Segment.created_at.desc(), Segment.id.desc()).all()


def update_segment(
    db: Session,
    segment_id: int,
    segment_data: SegmentUpdate,
    *,
    updated_by_id: int | None = None,
) -> Segment:
    segment = get_segment_by_id(db, segment_id)
    payload = segment_data.model_dump(exclude_unset=True)

    if "customer_id" in payload:
        customer = db.query(Customer).filter(Customer.id == payload["customer_id"]).first()
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found",
            )

    for field_name, field_value in payload.items():
        setattr(segment, field_name, field_value)

    segment.updated_by_id = updated_by_id

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to update segment",
        ) from exc

    db.refresh(segment)
    return segment


def delete_segment(db: Session, segment_id: int) -> None:
    segment = get_segment_by_id(db, segment_id)
    db.delete(segment)
    db.commit()


def get_segment_statistics(db: Session) -> dict[str, object]:
    segments = db.query(Segment).all()
    total_segments = len(segments)
    distribution = Counter(segment.segment_name for segment in segments if segment.segment_name)

    return {
        "total_segments": total_segments,
        "segment_distribution": [
            {"name": name, "value": count}
            for name, count in distribution.most_common()
        ],
        "active_segments": sum(1 for segment in segments if segment.status == "active"),
        "inactive_segments": sum(1 for segment in segments if segment.status != "active"),
    }