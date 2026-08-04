from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime

from fastapi import HTTPException, status
from sqlalchemy import and_, asc, desc, func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.customer import Customer
from schemas.customer import CustomerCreate, CustomerFilterParams, CustomerUpdate


_SORTABLE_COLUMNS = {
    "id": Customer.id,
    "customer_id": Customer.customer_id,
    "name": Customer.name,
    "email": Customer.email,
    "company": Customer.company,
    "country": Customer.country,
    "industry": Customer.industry,
    "subscription_plan": Customer.subscription_plan,
    "contract_type": Customer.contract_type,
    "monthly_charges": Customer.monthly_charges,
    "total_charges": Customer.total_charges,
    "tenure": Customer.tenure,
    "churn_probability": Customer.churn_probability,
    "risk_level": Customer.risk_level,
    "created_at": Customer.created_at,
    "updated_at": Customer.updated_at,
}


def _raise_conflict(message: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=message,
    )


def _apply_text_filter(query, column, value: str | None):
    if value:
        return query.filter(func.lower(column).like(f"%{value.lower()}%"))
    return query


def _sort_clause(sort_by: str, sort_order: str):
    column = _SORTABLE_COLUMNS.get(sort_by, Customer.created_at)
    return asc(column) if sort_order.lower() == "asc" else desc(column)


def _customer_exists_by_unique_fields(
    db: Session,
    *,
    customer_id: str,
    email: str,
    exclude_id: int | None = None,
) -> Customer | None:
    query = db.query(Customer).filter(
        or_(
            Customer.customer_id == customer_id,
            Customer.email == email,
        )
    )

    if exclude_id is not None:
        query = query.filter(Customer.id != exclude_id)

    return query.first()


def create_customer(
    db: Session,
    customer_data: CustomerCreate,
    *,
    created_by_id: int | None = None,
) -> Customer:
    existing_customer = _customer_exists_by_unique_fields(
        db,
        customer_id=customer_data.customer_id,
        email=str(customer_data.email),
    )

    if existing_customer is not None:
        if existing_customer.customer_id == customer_data.customer_id:
            _raise_conflict("Customer ID already exists")
        _raise_conflict("Customer email already exists")

    customer = Customer(
        customer_id=customer_data.customer_id,
        name=customer_data.name,
        email=str(customer_data.email),
        phone=customer_data.phone,
        company=customer_data.company,
        city=customer_data.city,
        country=customer_data.country,
        industry=customer_data.industry,
        age=customer_data.age,
        gender=customer_data.gender,
        subscription_plan=customer_data.subscription_plan,
        contract_type=customer_data.contract_type,
        join_date=customer_data.join_date,
        monthly_charges=customer_data.monthly_charges,
        total_charges=customer_data.total_charges,
        tenure=customer_data.tenure,
        payment_status=customer_data.payment_status,
        support_tickets=customer_data.support_tickets,
        last_login=customer_data.last_login,
        churn_probability=customer_data.churn_probability,
        risk_level=customer_data.risk_level,
        customer_lifetime_value=customer_data.customer_lifetime_value,
        expected_revenue=customer_data.expected_revenue,
        priority_score=customer_data.priority_score,
        created_by_id=created_by_id,
        updated_by_id=created_by_id,
    )

    db.add(customer)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer already exists",
        ) from exc

    db.refresh(customer)
    return customer


def get_customer_by_id(db: Session, customer_pk: int) -> Customer | None:
    return db.query(Customer).filter(Customer.id == customer_pk).first()


def get_customer_by_customer_id(db: Session, customer_id: str) -> Customer | None:
    return db.query(Customer).filter(Customer.customer_id == customer_id).first()


def list_customers(
    db: Session,
    filters: CustomerFilterParams,
) -> tuple[Sequence[Customer], int]:
    query = db.query(Customer)

    if filters.search:
        search_term = f"%{filters.search.lower()}%"
        query = query.filter(
            or_(
                func.lower(Customer.customer_id).like(search_term),
                func.lower(Customer.name).like(search_term),
                func.lower(Customer.email).like(search_term),
                func.lower(Customer.company).like(search_term),
                func.lower(Customer.city).like(search_term),
                func.lower(Customer.country).like(search_term),
                func.lower(Customer.industry).like(search_term),
            )
        )

    query = _apply_text_filter(query, Customer.company, filters.company)
    query = _apply_text_filter(query, Customer.country, filters.country)
    query = _apply_text_filter(query, Customer.industry, filters.industry)
    query = _apply_text_filter(query, Customer.subscription_plan, filters.subscription_plan)
    query = _apply_text_filter(query, Customer.contract_type, filters.contract_type)
    query = _apply_text_filter(query, Customer.risk_level, filters.risk_level)
    query = _apply_text_filter(query, Customer.payment_status, filters.payment_status)

    if filters.min_monthly_charges is not None:
        query = query.filter(Customer.monthly_charges >= filters.min_monthly_charges)
    if filters.max_monthly_charges is not None:
        query = query.filter(Customer.monthly_charges <= filters.max_monthly_charges)
    if filters.min_tenure is not None:
        query = query.filter(Customer.tenure >= filters.min_tenure)
    if filters.max_tenure is not None:
        query = query.filter(Customer.tenure <= filters.max_tenure)
    if filters.min_churn_probability is not None:
        query = query.filter(Customer.churn_probability >= filters.min_churn_probability)
    if filters.max_churn_probability is not None:
        query = query.filter(Customer.churn_probability <= filters.max_churn_probability)

    total = query.count()

    records = (
        query.order_by(_sort_clause(filters.sort_by, filters.sort_order))
        .offset((filters.page - 1) * filters.page_size)
        .limit(filters.page_size)
        .all()
    )

    return records, total


def update_customer(
    db: Session,
    customer_pk: int,
    customer_data: CustomerUpdate,
    *,
    updated_by_id: int | None = None,
) -> Customer:
    customer = get_customer_by_id(db, customer_pk)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    payload = customer_data.model_dump(exclude_unset=True)

    if "customer_id" in payload or "email" in payload:
        next_customer_id = payload.get("customer_id", customer.customer_id)
        next_email = str(payload.get("email", customer.email))
        existing_customer = _customer_exists_by_unique_fields(
            db,
            customer_id=next_customer_id,
            email=next_email,
            exclude_id=customer.id,
        )

        if existing_customer is not None:
            if existing_customer.customer_id == next_customer_id:
                _raise_conflict("Customer ID already exists")
            _raise_conflict("Customer email already exists")

    for field_name, field_value in payload.items():
        if field_name == "email" and field_value is not None:
            setattr(customer, field_name, str(field_value))
            continue
        setattr(customer, field_name, field_value)

    customer.updated_by_id = updated_by_id

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to update customer due to a unique constraint",
        ) from exc

    db.refresh(customer)
    return customer


def delete_customer(db: Session, customer_pk: int) -> None:
    customer = get_customer_by_id(db, customer_pk)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    db.delete(customer)
    db.commit()


def count_customers(db: Session) -> int:
    return db.query(Customer).count()


def count_active_customers(db: Session) -> int:
    return db.query(Customer).filter(Customer.risk_level != "high").count()
