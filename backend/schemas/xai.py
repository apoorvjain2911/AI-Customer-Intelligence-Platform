from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class XAIContribution(BaseModel):
    feature: str
    importance_score: float
    direction: str
    value: object | None = None


class XAIExplanationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: int
    customer_key: str
    customer_name: str
    company: str | None = None
    churn_probability: float
    risk_level: str
    recommendation: str
    top_features: list[XAIContribution]
    reason_for_churn: str
    business_explanation: str
    latest_prediction: dict | None = None