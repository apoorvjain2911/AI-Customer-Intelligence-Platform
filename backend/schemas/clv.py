from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CLVCustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: str
    name: str
    company: str | None = None
    subscription_plan: str | None = None
    contract_type: str | None = None
    monthly_charges: float
    tenure: int
    customer_lifetime_value: float
    expected_revenue: float
    priority_score: float
    churn_probability: float


class CLVSummaryResponse(BaseModel):
    total_customers: int
    average_customer_lifetime_value: float
    top_customers: list[CLVCustomerResponse]
    high_value_customers: list[CLVCustomerResponse]
    priority_customers: list[CLVCustomerResponse]