from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.db import get_db
from models.user import User
from schemas.segment import (
    SegmentCreate,
    SegmentListResponse,
    SegmentResponse,
    SegmentUpdate,
)
from services.segment_service import (
    assign_segment_for_customer,
    create_segment,
    delete_segment,
    get_segment_by_id,
    get_segment_statistics,
    list_segments,
    update_segment,
)

router = APIRouter(prefix="/segments", tags=["segments"])


@router.post("", response_model=SegmentResponse, status_code=status.HTTP_201_CREATED)
def create_segment_endpoint(
    segment: SegmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payload = segment.model_copy(update={"created_by_id": current_user.id})
    return create_segment(db, payload, updated_by_id=current_user.id)


@router.post("/assign/{customer_id}", response_model=SegmentResponse, status_code=status.HTTP_201_CREATED)
def assign_segment_endpoint(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return assign_segment_for_customer(db, customer_id, created_by_id=current_user.id)


@router.get("", response_model=SegmentListResponse)
def list_segments_endpoint(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    customer_id: int | None = Query(default=None),
    segment_name: str | None = Query(default=None, max_length=64),
    status_filter: str | None = Query(default=None, alias="status", max_length=32),
):
    records = list_segments(
        db,
        customer_id=customer_id,
        segment_name=segment_name,
        status_filter=status_filter,
    )
    return {"items": records, "total": len(records)}


@router.get("/{segment_id}", response_model=SegmentResponse)
def get_segment_endpoint(
    segment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_segment_by_id(db, segment_id)


@router.put("/{segment_id}", response_model=SegmentResponse)
def update_segment_endpoint(
    segment_id: int,
    segment: SegmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_segment(db, segment_id, segment, updated_by_id=current_user.id)


@router.delete("/{segment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_segment_endpoint(
    segment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    delete_segment(db, segment_id)
    return None


@router.get("/stats/summary")
def segment_statistics_endpoint(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_segment_statistics(db)