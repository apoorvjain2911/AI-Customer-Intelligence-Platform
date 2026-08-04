from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.db import get_db
from models.user import User
from schemas.customer import (
    CustomerCreate,
    CustomerFilterParams,
    CustomerListResponse,
    CustomerResponse,
    CustomerUpdate,
)
from services.customer_service import (
    create_customer,
    delete_customer,
    get_customer_by_id,
    list_customers,
    update_customer,
)

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer_endpoint(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_customer(db, customer, created_by_id=current_user.id)


@router.get("", response_model=CustomerListResponse)
def list_customers_endpoint(
    filters: CustomerFilterParams = Depends(),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    items, total = list_customers(db, filters)
    pages = max((total + filters.page_size - 1) // filters.page_size, 1) if total else 0

    return {
        "items": items,
        "total": total,
        "page": filters.page,
        "page_size": filters.page_size,
        "pages": pages,
    }


@router.get("/{customer_pk}", response_model=CustomerResponse)
def get_customer_endpoint(
    customer_pk: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    customer = get_customer_by_id(db, customer_pk)

    if customer is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return customer


@router.put("/{customer_pk}", response_model=CustomerResponse)
def update_customer_endpoint(
    customer_pk: int,
    customer: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_customer(db, customer_pk, customer, updated_by_id=current_user.id)


@router.delete("/{customer_pk}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer_endpoint(
    customer_pk: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    delete_customer(db, customer_pk)
    return None