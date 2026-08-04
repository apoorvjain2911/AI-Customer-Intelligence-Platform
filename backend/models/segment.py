from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.db import Base


class Segment(Base):
    __tablename__ = "segments"

    __table_args__ = (
        Index("ix_segments_customer_id", "customer_id"),
        Index("ix_segments_segment_name", "segment_name"),
        Index("ix_segments_cluster_label", "cluster_label"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )
    segment_name: Mapped[str] = mapped_column(String(64), nullable=False)
    cluster_label: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    centroid_distance: Mapped[float | None] = mapped_column(Float, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")

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

    customer = relationship("Customer", lazy="joined")
    created_by = relationship("User", foreign_keys=[created_by_id], lazy="joined")
    updated_by = relationship("User", foreign_keys=[updated_by_id], lazy="joined")

    def to_dict(self) -> dict[str, object | None]:
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "segment_name": self.segment_name,
            "cluster_label": self.cluster_label,
            "confidence_score": self.confidence_score,
            "centroid_distance": self.centroid_distance,
            "summary": self.summary,
            "status": self.status,
            "created_by_id": self.created_by_id,
            "updated_by_id": self.updated_by_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }