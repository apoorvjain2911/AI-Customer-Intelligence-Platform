from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerBase(BaseModel):
    customer_id: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=50)
    company: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=120)
    country: str | None = Field(default=None, max_length=120)
    industry: str | None = Field(default=None, max_length=120)
    age: int | None = Field(default=None, ge=0, le=150)
    gender: str | None = Field(default=None, max_length=32)
    subscription_plan: str | None = Field(default=None, max_length=120)
    contract_type: str | None = Field(default=None, max_length=120)
    join_date: date | None = None
    monthly_charges: float | None = Field(default=0.0, ge=0)
    total_charges: float | None = Field(default=0.0, ge=0)
    tenure: int | None = Field(default=0, ge=0)
    payment_status: str | None = Field(default=None, max_length=64)
    support_tickets: int | None = Field(default=0, ge=0)
    last_login: datetime | None = None
    churn_probability: float | None = Field(default=0.0, ge=0, le=1)
    risk_level: str = Field(default="low", max_length=32)
    customer_lifetime_value: float | None = Field(default=0.0, ge=0)
    expected_revenue: float | None = Field(default=0.0, ge=0)
    priority_score: float | None = Field(default=0.0, ge=0)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    customer_id: str | None = Field(default=None, min_length=1, max_length=64)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    company: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=120)
    country: str | None = Field(default=None, max_length=120)
    industry: str | None = Field(default=None, max_length=120)
    age: int | None = Field(default=None, ge=0, le=150)
    gender: str | None = Field(default=None, max_length=32)
    subscription_plan: str | None = Field(default=None, max_length=120)
    contract_type: str | None = Field(default=None, max_length=120)
    join_date: date | None = None
    monthly_charges: float | None = Field(default=None, ge=0)
    total_charges: float | None = Field(default=None, ge=0)
    tenure: int | None = Field(default=None, ge=0)
    payment_status: str | None = Field(default=None, max_length=64)
    support_tickets: int | None = Field(default=None, ge=0)
    last_login: datetime | None = None
    churn_probability: float | None = Field(default=None, ge=0, le=1)
    risk_level: str | None = Field(default=None, max_length=32)
    customer_lifetime_value: float | None = Field(default=None, ge=0)
    expected_revenue: float | None = Field(default=None, ge=0)
    priority_score: float | None = Field(default=None, ge=0)


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: str
    name: str
    email: EmailStr
    phone: str | None = None
    company: str | None = None
    city: str | None = None
    country: str | None = None
    industry: str | None = None
    age: int | None = None
    gender: str | None = None
    subscription_plan: str | None = None
    contract_type: str | None = None
    join_date: date | None = None
    monthly_charges: float | None = None
    total_charges: float | None = None
    tenure: int | None = None
    payment_status: str | None = None
    support_tickets: int | None = None
    last_login: datetime | None = None
    churn_probability: float | None = None
    risk_level: str
    customer_lifetime_value: float | None = None
    expected_revenue: float | None = None
    priority_score: float | None = None
    created_by_id: int | None = None
    updated_by_id: int | None = None
    created_at: datetime
    updated_at: datetime


class CustomerListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[CustomerResponse]
    total: int
    page: int
    page_size: int
    pages: int


class CustomerFilterParams(BaseModel):
    search: str | None = Field(default=None, max_length=255)
    company: str | None = Field(default=None, max_length=255)
    country: str | None = Field(default=None, max_length=120)
    industry: str | None = Field(default=None, max_length=120)
    subscription_plan: str | None = Field(default=None, max_length=120)
    contract_type: str | None = Field(default=None, max_length=120)
    risk_level: str | None = Field(default=None, max_length=32)
    payment_status: str | None = Field(default=None, max_length=64)
    min_monthly_charges: float | None = Field(default=None, ge=0)
    max_monthly_charges: float | None = Field(default=None, ge=0)
    min_tenure: int | None = Field(default=None, ge=0)
    max_tenure: int | None = Field(default=None, ge=0)
    min_churn_probability: float | None = Field(default=None, ge=0, le=1)
    max_churn_probability: float | None = Field(default=None, ge=0, le=1)
    sort_by: str = Field(default="created_at", max_length=64)
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)