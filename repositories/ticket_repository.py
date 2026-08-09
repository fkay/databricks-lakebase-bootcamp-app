from __future__ import annotations

from typing import Callable, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models.ticket import Ticket, TicketMessage

SessionFactory = Callable[[], Session]


class TicketRepository:
    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    def _session(self) -> Session:
        return self._session_factory()

    def list_tickets(self) -> list[Ticket]:
        with self._session() as session:
            return list(session.scalars(select(Ticket)
                                        .order_by(Ticket.created_at.desc())
                                        ).all())

    def get_ticket(self, ticket_id: int) -> Optional[Ticket]:
        with self._session() as session:
            return session.get(Ticket, ticket_id)

    def get_ticket_with_messages(self, ticket_id: int) -> Optional[Ticket]:
        with self._session() as session:
            return session.scalar(
                select(Ticket)
                .where(Ticket.ticket_id == ticket_id)
                .options(selectinload(Ticket.messages))
            )

    def create_ticket(self, ticket: Ticket) -> Ticket:
        with self._session() as session:
            session.add(ticket)
            session.commit()
            session.refresh(ticket)
            return ticket

    def add_message(self, message: TicketMessage) -> TicketMessage:
        with self._session() as session:
            session.add(message)
            session.commit()
            session.refresh(message)
            return message

    def update_ticket(self, ticket: Ticket) -> Ticket:
        with self._session() as session:
            managed_tkt = session.merge(ticket)
            session.commit()
            session.refresh(managed_tkt)
            return managed_tkt

    def delete_message(self, message_id: int) -> bool:
        with self._session() as session:
            message = session.get(TicketMessage, message_id)
            if message is None:
                return False
            session.delete(message)
            session.commit()
            return True
