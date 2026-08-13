from __future__ import annotations

import enum
from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketCategory(str, enum.Enum):
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    ACCESS_SECURITY = "access_security"
    INFRASTRUCTURE = "infrastructure"


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id: Mapped[int] = mapped_column(primary_key=True,
                                           autoincrement=True)
    title: Mapped[str] = mapped_column(String(200),
                                       nullable=False)
    status: Mapped[str] = mapped_column(String(30),
                                        nullable=False,
                                        default=TicketStatus.OPEN.value)
    category: Mapped[str] = mapped_column(
                                    String(50),
                                    nullable=False,
                                    default=TicketCategory.SOFTWARE.value)
    created_by: Mapped[str] = mapped_column(String(200),
                                            nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now(),
                                                 nullable=False)

    messages: Mapped[List["TicketMessage"]] = relationship(
                        back_populates="ticket",
                        cascade="all, delete-orphan")


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    message_id: Mapped[int] = mapped_column(primary_key=True,
                                            autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.ticket_id"),
                                           nullable=False)
    message_text: Mapped[str] = mapped_column(Text,
                                              nullable=False)
    author: Mapped[str] = mapped_column(String(120),
                                        nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now(),
                                                 nullable=False)

    ticket: Mapped[Ticket] = relationship(back_populates="messages")
