from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.customer import Customer


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _days_since(value: datetime | None) -> int | None:
    if value is None:
        return None

    now = datetime.now(timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return max(0, (now - value).days)


def calculate_customer_lifetime_value(customer: Customer) -> float:
    monthly_charges = _safe_float(customer.monthly_charges)
    tenure = _safe_int(customer.tenure)
    churn_probability = min(max(_safe_float(customer.churn_probability), 0.0), 1.0)

    retention_multiplier = max(0.15, 1.0 - churn_probability)
    lifecycle_bonus = 1.0 + min(tenure / 48.0, 1.5)
    revenue_component = monthly_charges * max(tenure, 1)

    clv = revenue_component * retention_multiplier * lifecycle_bonus
    return round(clv, 2)


def calculate_expected_revenue(customer: Customer) -> float:
    clv = calculate_customer_lifetime_value(customer)
    tenure = _safe_int(customer.tenure)

    projected_months = max(6, 24 - min(tenure, 18))
    projected_revenue = clv / max(tenure or 1, 1) * projected_months
    return round(projected_revenue, 2)


def calculate_priority_score(customer: Customer) -> float:
    clv = calculate_customer_lifetime_value(customer)
    churn_probability = min(max(_safe_float(customer.churn_probability), 0.0), 1.0)
    support_tickets = _safe_int(customer.support_tickets)
    inactivity_days = _days_since(customer.last_login)

    risk_penalty = churn_probability * 40.0
    support_penalty = min(support_tickets * 2.5, 25.0)
    inactivity_penalty = min((inactivity_days or 0) / 10.0, 20.0)

    score = min(100.0, (clv / 100.0) - risk_penalty - support_penalty - inactivity_penalty)
    return round(max(score, 0.0), 2)


def refresh_customer_value_metrics(customer: Customer) -> Customer:
    customer.customer_lifetime_value = calculate_customer_lifetime_value(customer)
    customer.expected_revenue = calculate_expected_revenue(customer)
    customer.priority_score = calculate_priority_score(customer)
    return customer


def _customer_metrics_snapshot(customer: Customer) -> dict[str, Any]:
    clv = calculate_customer_lifetime_value(customer)
    expected_revenue = calculate_expected_revenue(customer)
    priority_score = calculate_priority_score(customer)

    return {
        "id": customer.id,
        "customer_id": customer.customer_id,
        "name": customer.name,
        "company": customer.company,
        "subscription_plan": customer.subscription_plan,
        "contract_type": customer.contract_type,
        "monthly_charges": _safe_float(customer.monthly_charges),
        "tenure": _safe_int(customer.tenure),
        "customer_lifetime_value": clv,
        "expected_revenue": expected_revenue,
        "priority_score": priority_score,
        "churn_probability": round(_safe_float(customer.churn_probability), 4),
    }


def update_customer_value_metrics(db: Session, customer_id: int) -> Customer:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    refresh_customer_value_metrics(customer)
    db.commit()
    db.refresh(customer)
    return customer


def get_customer_clv_summary(db: Session) -> dict[str, Any]:
    customers = db.query(Customer).all()

    scored_customers = [
        _customer_metrics_snapshot(customer)
        for customer in customers
    ]

    scored_customers.sort(
        key=lambda item: (
            _safe_float(item["priority_score"]),
            _safe_float(item["customer_lifetime_value"]),
        ),
        reverse=True,
    )

    top_customers = scored_customers[:20]
    average_clv = (
        round(
            sum(_safe_float(customer["customer_lifetime_value"]) for customer in scored_customers)
            / len(scored_customers),
            2,
        )
        if scored_customers
        else 0.0
    )

    return {
        "total_customers": len(scored_customers),
        "average_customer_lifetime_value": average_clv,
        "top_customers": top_customers,
        "high_value_customers": [customer for customer in top_customers if _safe_float(customer["customer_lifetime_value"]) >= average_clv],
        "priority_customers": [customer for customer in top_customers if _safe_float(customer["priority_score"]) >= 50],
    }


def get_top_customers_by_clv(db: Session, limit: int = 20) -> Sequence[dict[str, Any]]:
    summary = get_customer_clv_summary(db)
    return summary["top_customers"][:limit]
