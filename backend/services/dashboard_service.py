from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.models import Prediction
from models.customer import Customer
from services.preprocess import ID_COLUMN, LATEST_UPLOAD_PATH, read_csv
from services.recommendation import get_risk_level


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _percent_change(current: int | float, previous: int | float) -> float:
    current_value = float(current or 0)
    previous_value = float(previous or 0)

    if previous_value == 0:
        return 100.0 if current_value > 0 else 0.0

    return round(((current_value - previous_value) / previous_value) * 100, 2)


def _bucket_risk_level(probability: float | None, current_risk: str | None = None) -> str:
    if current_risk:
        normalized = current_risk.strip().lower()
        if normalized in {"low", "medium", "high"}:
            return normalized.capitalize()

    return get_risk_level(float(probability or 0)).capitalize()


def _load_dataframe_fallback() -> pd.DataFrame | None:
    if not LATEST_UPLOAD_PATH.exists():
        return None

    frame = read_csv(LATEST_UPLOAD_PATH)
    if ID_COLUMN not in frame.columns:
        frame[ID_COLUMN] = [f"customer-{index + 1}" for index in range(len(frame))]
    return frame


def _build_fallback_summary() -> dict[str, Any]:
    frame = _load_dataframe_fallback()

    if frame is None or frame.empty:
        return {
            "total_customers": 0,
            "active_customers": 0,
            "at_risk_customers": 0,
            "monthly_revenue": 0,
            "average_revenue": 0,
            "retention_rate": 0,
            "customer_growth": 0,
            "revenue_trend": [],
            "monthly_churn": [],
            "customer_growth_data": [],
            "subscription_distribution": [],
            "contract_distribution": [],
            "age_distribution": [],
            "risk_distribution": [],
            "top_high_risk_customers": [],
            "latest_customers": [],
            "latest_predictions": [],
            "message": "Upload a CSV file or create customer records to begin.",
        }

    total_customers = int(len(frame))
    at_risk_customers = int(
        sum(
            1
            for probability in frame.get("Churn", pd.Series(dtype=object)).fillna(0)
            if str(probability).lower() in {"yes", "1", "true"}
        )
    )

    monthly_revenue = _safe_float(
        pd.to_numeric(frame.get("MonthlyCharges", pd.Series(dtype=float)), errors="coerce")
        .fillna(0)
        .sum()
    )
    average_revenue = round(monthly_revenue / total_customers, 2) if total_customers else 0
    retention_rate = round(((total_customers - at_risk_customers) / total_customers) * 100, 2) if total_customers else 0

    subscription_distribution = (
        frame.get("SubscriptionPlan")
        .fillna("Unknown")
        .value_counts()
        .head(8)
        .reset_index()
        .rename(columns={"index": "name", "SubscriptionPlan": "value"})
        .to_dict(orient="records")
        if "SubscriptionPlan" in frame.columns
        else []
    )

    contract_distribution = (
        frame.get("Contract")
        .fillna("Unknown")
        .value_counts()
        .head(8)
        .reset_index()
        .rename(columns={"index": "name", "Contract": "value"})
        .to_dict(orient="records")
        if "Contract" in frame.columns
        else []
    )

    age_distribution = (
        pd.cut(pd.to_numeric(frame.get("SeniorCitizen", pd.Series(dtype=float)), errors="coerce").fillna(0), bins=[-1, 0, 1], labels=["Adult", "Senior"])
        .value_counts()
        .reset_index()
        .rename(columns={"index": "name", 0: "value"})
        .to_dict(orient="records")
        if "SeniorCitizen" in frame.columns
        else []
    )

    risk_distribution = [
        {"name": "Low", "value": total_customers - at_risk_customers},
        {"name": "High", "value": at_risk_customers},
    ]

    return {
        "total_customers": total_customers,
        "active_customers": total_customers - at_risk_customers,
        "at_risk_customers": at_risk_customers,
        "monthly_revenue": round(monthly_revenue, 2),
        "average_revenue": average_revenue,
        "retention_rate": retention_rate,
        "customer_growth": 0,
        "revenue_trend": [],
        "monthly_churn": [],
        "customer_growth_data": [],
        "subscription_distribution": subscription_distribution,
        "contract_distribution": contract_distribution,
        "age_distribution": age_distribution,
        "risk_distribution": risk_distribution,
        "top_high_risk_customers": [],
        "latest_customers": [],
        "latest_predictions": [],
    }


def _top_risk_customers(customers: list[Customer], limit: int = 10) -> list[dict[str, Any]]:
    ranked = sorted(
        customers,
        key=lambda customer: (
            _safe_float(customer.churn_probability),
            _safe_float(customer.priority_score),
        ),
        reverse=True,
    )

    result: list[dict[str, Any]] = []
    for customer in ranked[:limit]:
        result.append(
            {
                "id": customer.id,
                "customer_id": customer.customer_id,
                "name": customer.name,
                "email": customer.email,
                "company": customer.company,
                "risk_level": _bucket_risk_level(customer.churn_probability, customer.risk_level),
                "churn_probability": round(_safe_float(customer.churn_probability), 4),
                "priority_score": round(_safe_float(customer.priority_score), 2),
            }
        )
    return result


def _latest_customers(customers: list[Customer], limit: int = 10) -> list[dict[str, Any]]:
    ordered = sorted(customers, key=lambda customer: customer.created_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return [customer.to_dict() for customer in ordered[:limit]]


def _latest_predictions(predictions: list[Prediction], limit: int = 10) -> list[dict[str, Any]]:
    ordered = sorted(predictions, key=lambda prediction: prediction.created_at or datetime.min, reverse=True)
    return [prediction.to_dict() for prediction in ordered[:limit]]


def _distribution_from_customers(customers: list[Customer], field_name: str, limit: int = 10) -> list[dict[str, Any]]:
    values = [getattr(customer, field_name) for customer in customers if getattr(customer, field_name)]
    counts = Counter(values)
    return [
        {"name": name, "value": count}
        for name, count in counts.most_common(limit)
    ]


def _age_distribution(customers: list[Customer]) -> list[dict[str, Any]]:
    buckets = Counter()
    for customer in customers:
        age = customer.age
        if age is None:
            buckets["Unknown"] += 1
        elif age < 25:
            buckets["18-24"] += 1
        elif age < 35:
            buckets["25-34"] += 1
        elif age < 45:
            buckets["35-44"] += 1
        elif age < 55:
            buckets["45-54"] += 1
        else:
            buckets["55+"] += 1

    return [
        {"name": name, "value": count}
        for name, count in buckets.items()
    ]


def _monthly_revenue(customers: list[Customer]) -> float:
    return round(sum(_safe_float(customer.monthly_charges) for customer in customers), 2)


def _customer_growth(customers: list[Customer]) -> tuple[int, list[dict[str, Any]]]:
    monthly_counts: dict[str, int] = {}
    for customer in customers:
        if customer.created_at is None:
            continue
        month_key = customer.created_at.strftime("%Y-%m")
        monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1

    ordered_months = sorted(monthly_counts.items())
    growth_data = [{"name": month, "value": count} for month, count in ordered_months]

    if len(ordered_months) < 2:
        return 0, growth_data

    previous = ordered_months[-2][1]
    current = ordered_months[-1][1]
    return int(_percent_change(current, previous)), growth_data


def _revenue_trend(customers: list[Customer]) -> list[dict[str, Any]]:
    monthly_totals: dict[str, float] = {}
    for customer in customers:
        if customer.created_at is None:
            continue
        month_key = customer.created_at.strftime("%Y-%m")
        monthly_totals[month_key] = monthly_totals.get(month_key, 0.0) + _safe_float(customer.monthly_charges)

    return [
        {"name": month, "value": round(total, 2)}
        for month, total in sorted(monthly_totals.items())
    ]


def _monthly_churn(customers: list[Customer]) -> list[dict[str, Any]]:
    monthly_counts: dict[str, int] = {}
    for customer in customers:
        if customer.created_at is None:
            continue
        if _bucket_risk_level(customer.churn_probability, customer.risk_level) != "High":
            continue
        month_key = customer.created_at.strftime("%Y-%m")
        monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1

    return [{"name": month, "value": count} for month, count in sorted(monthly_counts.items())]


def build_dashboard_summary(db: Session | None = None) -> dict[str, Any]:
    if db is None:
        return _build_fallback_summary()

    customers = db.query(Customer).order_by(Customer.created_at.desc(), Customer.id.desc()).all()
    predictions = db.query(Prediction).order_by(Prediction.created_at.desc(), Prediction.id.desc()).all()

    total_customers = len(customers)
    active_customers = sum(1 for customer in customers if _bucket_risk_level(customer.churn_probability, customer.risk_level) != "High")
    at_risk_customers = total_customers - active_customers
    monthly_revenue = _monthly_revenue(customers)
    average_revenue = round(monthly_revenue / total_customers, 2) if total_customers else 0
    retention_rate = round((active_customers / total_customers) * 100, 2) if total_customers else 0
    customer_growth, customer_growth_data = _customer_growth(customers)

    revenue_trend = _revenue_trend(customers)
    monthly_churn = _monthly_churn(customers)

    subscription_distribution = _distribution_from_customers(customers, "subscription_plan")
    contract_distribution = _distribution_from_customers(customers, "contract_type")
    age_distribution = _age_distribution(customers)
    risk_distribution = [
        {"name": "Low", "value": active_customers},
        {"name": "High", "value": at_risk_customers},
    ]

    return {
        "total_customers": total_customers,
        "active_customers": active_customers,
        "at_risk_customers": at_risk_customers,
        "monthly_revenue": monthly_revenue,
        "average_revenue": average_revenue,
        "retention_rate": retention_rate,
        "customer_growth": customer_growth,
        "revenue_trend": revenue_trend,
        "monthly_churn": monthly_churn,
        "customer_growth_data": customer_growth_data,
        "subscription_distribution": subscription_distribution,
        "contract_distribution": contract_distribution,
        "age_distribution": age_distribution,
        "risk_distribution": risk_distribution,
        "top_high_risk_customers": _top_risk_customers(customers),
        "latest_customers": _latest_customers(customers),
        "latest_predictions": _latest_predictions(predictions),
    }