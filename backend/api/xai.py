from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.db import get_db
from models.user import User
from schemas.xai import XAIExplanationResponse
from services.xai_service import get_customer_explanation

router = APIRouter(prefix="/xai", tags=["xai"])


@router.get("/customers/{customer_id}", response_model=XAIExplanationResponse)
def explain_customer_endpoint(
    customer_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_customer_explanation(db, customer_id)