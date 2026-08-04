from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CopilotRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)
    customer_id: int | None = None
    customer_name: str | None = Field(default=None, max_length=255)
    provider: str | None = Field(default=None, max_length=32)


class CopilotContextResponse(BaseModel):
    prompt: str
    customer: dict[str, Any] | None = None
    portfolio: dict[str, Any]
    explanation: dict[str, Any] | None = None


class CopilotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    provider: str
    response: str
    context: CopilotContextResponse