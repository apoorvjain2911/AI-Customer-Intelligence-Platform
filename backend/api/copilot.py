from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.db import get_db
from models.user import User
from schemas.copilot import CopilotRequest, CopilotResponse
from services.copilot_service import generate_copilot_response

router = APIRouter(prefix="/copilot", tags=["copilot"])


@router.post("/chat", response_model=CopilotResponse)
def copilot_chat_endpoint(
    payload: CopilotRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return generate_copilot_response(
        db,
        prompt=payload.prompt,
        customer_id=payload.customer_id,
        customer_name=payload.customer_name,
        provider=payload.provider,
    )