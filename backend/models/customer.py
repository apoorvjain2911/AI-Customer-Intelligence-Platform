from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.db import Base


class Customer(Base):
    __tablename__ = "customers"

    __table_args__ = (
        Index("ix_customers_customer_id", "customer_id", unique=True),
        Index("ix_customers_email", "email", unique=True),
        Index("ix_customers_risk_level", "risk_level"),
        Index("ix_customers_company", "company"),
        Index("ix_customers_country", "country"),
        Index("ix_customers_subscription_plan", "subscription_plan"),
        Index("ix_customers_contract_type", "contract_type"),
        Index("ix_customers_join_date", "join_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[str] = mapped_column(String(64), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True)

    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(32), nullable=True)
    subscription_plan: Mapped[str | None] = mapped_column(String(120), nullable=True)
    contract_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    join_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    monthly_charges: Mapped[float | None] = mapped_column(Float, nullable=True, default=0.0)
    total_charges: Mapped[float | None] = mapped_column(Float, nullable=True, default=0.0)
    tenure: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)
    payment_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    support_tickets: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    churn_probability: Mapped[float | None] = mapped_column(Float, nullable=True, default=0.0)
    risk_level: Mapped[str] = mapped_column(String(32), nullable=False, default="low")
    customer_lifetime_value: Mapped[float | None] = mapped_column(Float, nullable=True, default=0.0)
    expected_revenue: Mapped[float | None] = mapped_column(Float, nullable=True, default=0.0)
    priority_score: Mapped[float | None] = mapped_column(Float, nullable=True, default=0.0)

    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    created_by = relationship(
        "User",
        foreign_keys=[created_by_id],
        lazy="joined",
    )
    updated_by = relationship(
        "User",
        foreign_keys=[updated_by_id],
        lazy="joined",
    )

    def to_dict(self) -> dict[str, object | None]:
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "company": self.company,
            "city": self.city,
            "country": self.country,
            "industry": self.industry,
            "age": self.age,
            "gender": self.gender,
            "subscription_plan": self.subscription_plan,
            "contract_type": self.contract_type,
            "join_date": self.join_date.isoformat() if self.join_date else None,
            "monthly_charges": self.monthly_charges,
            "total_charges": self.total_charges,
            "tenure": self.tenure,
            "payment_status": self.payment_status,
            "support_tickets": self.support_tickets,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "churn_probability": self.churn_probability,
            "risk_level": self.risk_level,
            "customer_lifetime_value": self.customer_lifetime_value,
            "expected_revenue": self.expected_revenue,
            "priority_score": self.priority_score,
            "created_by_id": self.created_by_id,
            "updated_by_id": self.updated_by_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }