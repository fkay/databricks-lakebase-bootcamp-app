from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TicketCreateRequest(BaseModel):
    title: str = Field(min_length=1)
    created_by: str = Field(min_length=1)
    category: Literal["hardware", "software", "network", "access_security", "infrastructure"] = "software"


class TicketMessageCreateRequest(BaseModel):
    author: str = Field(default="customer", min_length=1)
    message_text: str = Field(min_length=1)


class TicketStatusUpdateRequest(BaseModel):
    status: Literal["open", "in_progress", "resolved", "closed"]


class TicketMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    message_id: int
    ticket_id: int
    author: str
    message_text: str
    created_at: datetime


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_id: int
    title: str
    status: str
    category: str
    created_by: str
    created_at: datetime


class TicketDetailResponse(TicketResponse):
    model_config = ConfigDict(from_attributes=True)

    messages: list[TicketMessageResponse]
