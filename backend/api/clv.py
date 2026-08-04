from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.db import get_db
from models.user import User
from schemas.clv import CLVSummaryResponse, CLVCustomerResponse
from services.clv_service import (
    get_customer_clv_summary,
    get_top_customers_by_clv,
    update_customer_value_metrics,
)

router = APIRouter(prefix="/clv", tags=["clv"])


@router.get("/summary", response_model=CLVSummaryResponse)
def clv_summary_endpoint(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_customer_clv_summary(db)


@router.get("/top", response_model=list[CLVCustomerResponse])
def clv_top_customers_endpoint(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_top_customers_by_clv(db)


@router.post("/refresh/{customer_id}", status_code=status.HTTP_200_OK)
def clv_refresh_endpoint(
    customer_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    customer = update_customer_value_metrics(db, customer_id)
    return {
        "status": "success",
        "message": "Customer CLV metrics updated",
        "customer": customer.to_dict(),
    }