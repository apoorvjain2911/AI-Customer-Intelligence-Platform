from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import joblib
import pandas as pd
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from database.models import Prediction
from models.customer import Customer
from services.preprocess import MODEL_PATH, PIPELINE_PATH, coerce_input_frame
from services.recommendation import get_recommendation, get_risk_level


@dataclass(frozen=True)
class FeatureContribution:
    feature: str
    importance_score: float
    direction: str
    value: Any


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _latest_prediction(db: Session, customer_key: str) -> Prediction | None:
    return (
        db.query(Prediction)
        .filter(Prediction.customer_id == customer_key)
        .order_by(Prediction.created_at.desc(), Prediction.id.desc())
        .first()
    )


def _alias_value(customer: Customer, aliases: tuple[str, ...], default: Any = None) -> Any:
    for alias in aliases:
        value = getattr(customer, alias, None)
        if value not in (None, ""):
            return value
    return default


def _customer_to_training_frame(customer: Customer, expected_columns: list[str]) -> pd.DataFrame:
    alias_map: dict[str, tuple[str, ...]] = {
        "customerID": ("customer_id",),
        "gender": ("gender",),
        "SeniorCitizen": ("age",),
        "Partner": ("company",),
        "Dependents": ("support_tickets",),
        "tenure": ("tenure",),
        "PhoneService": ("phone",),
        "MultipleLines": ("support_tickets",),
        "InternetService": ("subscription_plan",),
        "OnlineSecurity": ("industry",),
        "OnlineBackup": ("industry",),
        "DeviceProtection": ("industry",),
        "TechSupport": ("support_tickets",),
        "StreamingTV": ("subscription_plan",),
        "StreamingMovies": ("subscription_plan",),
        "Contract": ("contract_type",),
        "PaperlessBilling": ("payment_status",),
        "PaymentMethod": ("payment_status",),
        "MonthlyCharges": ("monthly_charges",),
        "TotalCharges": ("total_charges",),
    }

    row: dict[str, Any] = {}
    for column in expected_columns:
        aliases = alias_map.get(column, ())
        if aliases:
            row[column] = _alias_value(customer, aliases)
        else:
            row[column] = getattr(customer, column, None)

    frame = pd.DataFrame([row])
    return coerce_input_frame(frame, expected_columns)


@lru_cache(maxsize=1)
def _load_artifacts() -> tuple[Any, Any]:
    if not MODEL_PATH.exists() or not PIPELINE_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Train a model before requesting explanations.",
        )

    model = joblib.load(MODEL_PATH)
    pipeline = joblib.load(PIPELINE_PATH)
    return model, pipeline


def _load_shap_module():
    try:
        import shap  # type: ignore

        return shap
    except Exception as exc:  # pragma: no cover - dependency specific guard
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SHAP is not available in the current environment.",
        ) from exc


def _predict_probability(model: Any, transformed_frame: Any) -> float:
    probabilities = model.predict_proba(transformed_frame)
    if len(probabilities) == 0:
        return 0.0
    return _safe_float(probabilities[0][1])




import numpy as np

def _explain_contributions(
    shap_values: Any,
    feature_names: list[str],
    feature_row: pd.DataFrame,
    limit: int = 5,
) -> list[FeatureContribution]:

    # Handle different SHAP output formats
    if isinstance(shap_values, list):
        values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
    elif hasattr(shap_values, "values"):
        values = shap_values.values
    else:
        values = shap_values

    values = np.asarray(values)
    values = np.squeeze(values)

    # If still 2D, take first sample
    if values.ndim == 2:
        values = values[0]

    indexed = sorted(
        zip(feature_names, values),
        key=lambda x: abs(float(np.asarray(x[1]).item())),
        reverse=True,
    )[:limit]

    contributions: list[FeatureContribution] = []

    for feature, contribution in indexed:

        contribution = float(np.asarray(contribution).item())

        raw_value = feature_row.iloc[0].get(feature)

        # Convert numpy scalars to Python scalars
        if isinstance(raw_value, np.generic):
            raw_value = raw_value.item()

        contributions.append(
            FeatureContribution(
                feature=str(feature),
                importance_score=round(abs(contribution), 6),
                direction=(
                    "increases churn risk"
                    if contribution > 0
                    else "reduces churn risk"
                ),
                value=raw_value,
            )
        )

    return contributions

def get_customer_explanation(db: Session, customer_pk: int) -> dict[str, Any]:
    customer = db.query(Customer).filter(Customer.id == customer_pk).first()

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    model, pipeline = _load_artifacts()
    shap = _load_shap_module()

    expected_columns = list(getattr(pipeline, "feature_names_in_", []))
    if not expected_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The trained preprocessing pipeline does not expose input feature names.",
        )

    feature_row = _customer_to_training_frame(customer, expected_columns)
    transformed = pipeline.transform(feature_row)

    if hasattr(model, "predict_proba"):
        churn_probability = _predict_probability(model, transformed)
    else:
        churn_probability = _safe_float(customer.churn_probability)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(transformed)
    contributions = _explain_contributions(shap_values, expected_columns, feature_row)

    risk_level = get_risk_level(churn_probability)
    recommendation = get_recommendation(risk_level)

    top_driver = contributions[0] if contributions else None
    secondary_driver = contributions[1] if len(contributions) > 1 else None

    reason_parts = []
    if top_driver is not None:
        reason_parts.append(
            f"{top_driver.feature} {top_driver.direction}"
        )
    if secondary_driver is not None:
        reason_parts.append(
            f"{secondary_driver.feature} {secondary_driver.direction}"
        )

    reason_for_churn = "; ".join(reason_parts) if reason_parts else "The model does not have enough signal to isolate a dominant churn driver."

    business_explanation = (
        f"This customer is classified as {risk_level.lower()} risk. "
        f"The strongest model drivers are {', '.join(item.feature for item in contributions[:3]) or 'the available customer attributes'}. "
        f"Recommended action: {recommendation}"
    )

    latest_prediction = _latest_prediction(db, customer.customer_id)

    return {
        "customer_id": customer.id,
        "customer_key": customer.customer_id,
        "customer_name": customer.name,
        "company": customer.company,
        "churn_probability": round(churn_probability, 4),
        "risk_level": risk_level,
        "recommendation": recommendation,
        "top_features": [
            {
                "feature": item.feature,
                "importance_score": item.importance_score,
                "direction": item.direction,
                "value": item.value,
            }
            for item in contributions
        ],
        "reason_for_churn": reason_for_churn,
        "business_explanation": business_explanation,
        "latest_prediction": latest_prediction.to_dict() if latest_prediction else None,
    }