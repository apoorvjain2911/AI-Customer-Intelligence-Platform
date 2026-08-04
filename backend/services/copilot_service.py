from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Sequence
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from database.models import Prediction
from models.customer import Customer
from services.clv_service import calculate_customer_lifetime_value, calculate_priority_score
from services.recommendation import get_recommendation, get_risk_level
from services.xai_service import get_customer_explanation


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _customer_snapshot(customer: Customer) -> dict[str, Any]:
    churn_probability = _safe_float(customer.churn_probability)
    risk_level = get_risk_level(churn_probability)
    clv = calculate_customer_lifetime_value(customer)
    priority_score = calculate_priority_score(customer)

    return {
        "id": customer.id,
        "customer_id": customer.customer_id,
        "name": customer.name,
        "email": customer.email,
        "company": customer.company,
        "city": customer.city,
        "country": customer.country,
        "industry": customer.industry,
        "subscription_plan": customer.subscription_plan,
        "contract_type": customer.contract_type,
        "monthly_charges": _safe_float(customer.monthly_charges),
        "total_charges": _safe_float(customer.total_charges),
        "tenure": customer.tenure or 0,
        "support_tickets": customer.support_tickets or 0,
        "last_login": customer.last_login.isoformat() if customer.last_login else None,
        "churn_probability": round(churn_probability, 4),
        "risk_level": risk_level,
        "recommendation": get_recommendation(risk_level),
        "customer_lifetime_value": clv,
        "priority_score": priority_score,
    }


def _latest_prediction_snapshot(db: Session, customer_key: str) -> dict[str, Any] | None:
    prediction = (
        db.query(Prediction)
        .filter(Prediction.customer_id == customer_key)
        .order_by(desc(Prediction.created_at), desc(Prediction.id))
        .first()
    )

    return prediction.to_dict() if prediction else None


def _high_risk_customers(customers: Sequence[Customer], limit: int = 10) -> list[dict[str, Any]]:
    ranked = sorted(
        customers,
        key=lambda customer: (
            _safe_float(customer.churn_probability),
            calculate_priority_score(customer),
        ),
        reverse=True,
    )

    return [_customer_snapshot(customer) for customer in ranked[:limit]]


def _build_executive_summary(customers: Sequence[Customer], predictions: Sequence[Prediction]) -> str:
    total_customers = len(customers)
    active_customers = sum(1 for customer in customers if _safe_float(customer.churn_probability) < 0.5)
    at_risk_customers = total_customers - active_customers
    average_clv = (
        round(
            sum(calculate_customer_lifetime_value(customer) for customer in customers) / total_customers,
            2,
        )
        if total_customers
        else 0.0
    )
    latest_prediction = predictions[0] if predictions else None

    summary_parts = [
        f"The portfolio contains {total_customers} customers.",
        f"{active_customers} are currently healthy and {at_risk_customers} are at elevated churn risk.",
        f"Average CLV is {average_clv:.2f}.",
    ]

    if latest_prediction is not None:
        summary_parts.append(
            f"The latest prediction for customer {latest_prediction.customer_id} was {latest_prediction.risk.lower()} risk."
        )

    return " ".join(summary_parts)


def build_copilot_context(
    db: Session,
    prompt: str,
    customer_id: int | None = None,
    customer_name: str | None = None,
) -> dict[str, Any]:
    customers_query = db.query(Customer).order_by(desc(Customer.created_at), desc(Customer.id))

    customers = customers_query.all()
    predictions = (
        db.query(Prediction)
        .order_by(desc(Prediction.created_at), desc(Prediction.id))
        .limit(25)
        .all()
    )

    selected_customer: Customer | None = None
    if customer_id is not None:
        selected_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    elif customer_name:
        selected_customer = (
            db.query(Customer)
            .filter(Customer.name.ilike(f"%{customer_name.strip()}%"))
            .order_by(desc(Customer.created_at), desc(Customer.id))
            .first()
        )

    customer_snapshot = _customer_snapshot(selected_customer) if selected_customer else None
    latest_predictions = [prediction.to_dict() for prediction in predictions[:10]]

    return {
        "prompt": prompt,
        "customer": customer_snapshot,
        "portfolio": {
            "total_customers": len(customers),
            "high_risk_customers": _high_risk_customers(customers),
            "latest_predictions": latest_predictions,
            "executive_summary": _build_executive_summary(customers, predictions),
        },
        "explanation": get_customer_explanation(db, selected_customer.id) if selected_customer else None,
    }


def _build_messages(context: dict[str, Any]) -> list[dict[str, str]]:
    customer_block = json.dumps(context.get("customer"), indent=2, default=str)
    portfolio_block = json.dumps(context.get("portfolio"), indent=2, default=str)

    system_message = (
        "You are an AI customer success copilot for a Salesforce-like CRM. "
        "Use the provided customer, prediction, CLV, and explanation context to answer succinctly, "
        "with practical retention actions, executive-ready tone, and no fabricated facts."
    )

    user_message = (
        f"Prompt: {context.get('prompt')}\n\n"
        f"Customer context:\n{customer_block}\n\n"
        f"Portfolio context:\n{portfolio_block}\n\n"
        f"Explanation context:\n{json.dumps(context.get('explanation'), indent=2, default=str)}"
    )

    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]


def _call_openai(messages: list[dict[str, str]]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OPENAI_API_KEY is not configured.",
        )

    payload = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "messages": messages,
        "temperature": 0.3,
    }

    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"OpenAI request failed: {detail}",
        ) from exc

    choices = response_payload.get("choices", [])
    if not choices:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenAI returned an empty response.",
        )

    message = choices[0].get("message", {})
    return str(message.get("content", "")).strip()


def _call_groq(messages: list[dict[str, str]]) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GROQ_API_KEY is not configured.",
        )

    payload = {
        "model": os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile"),
        "messages": messages,
        "temperature": 0.3,
    }

    request = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Groq request failed: {detail}",
        ) from exc

    choices = response_payload.get("choices", [])
    if not choices:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Groq returned an empty response.",
        )

    message = choices[0].get("message", {})
    return str(message.get("content", "")).strip()


def generate_copilot_response(
    db: Session,
    prompt: str,
    customer_id: int | None = None,
    customer_name: str | None = None,
    provider: str | None = None,
) -> dict[str, Any]:
    context = build_copilot_context(
        db,
        prompt=prompt,
        customer_id=customer_id,
        customer_name=customer_name,
    )

    messages = _build_messages(context)
    provider_choice = (provider or os.getenv("COPILOT_PROVIDER", "local")).strip().lower()

    if provider_choice == "openai":
        response_text = _call_openai(messages)
    elif provider_choice == "groq":
        response_text = _call_groq(messages)
    else:
        response_text = (
            f"Prompt received: {prompt}. "
            f"Customer summary: {context['customer']['name'] if context['customer'] else 'No customer selected'}. "
            f"Executive summary: {context['portfolio']['executive_summary']}"
        )

    return {
        "provider": provider_choice,
        "response": response_text,
        "context": context,
    }