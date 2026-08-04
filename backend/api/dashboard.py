from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import get_db
from services.dashboard_service import build_dashboard_summary

router = APIRouter(prefix="", tags=["dashboard"])


@router.get("/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    return build_dashboard_summary(db)