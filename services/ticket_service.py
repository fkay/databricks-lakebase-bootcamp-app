from __future__ import annotations

from datetime import datetime, timezone

from models.ticket import Ticket, TicketMessage, TicketStatus
from repositories.ticket_repository import TicketRepository


class TicketService:
    def __init__(self, repository: TicketRepository) -> None:
        self.repository = repository

    def list_tickets(self) -> list[Ticket]:
        return self.repository.list_tickets()

    def get_ticket(self, ticket_id: int) -> Ticket | None:
        return self.repository.get_ticket(ticket_id)

    def get_ticket_with_messages(self, ticket_id: int) -> Ticket | None:
        return self.repository.get_ticket_with_messages(ticket_id)

    def create_ticket(self, title: str, created_by: str,
                      category: str = "software") -> Ticket:
        ticket = Ticket(
            title=title,
            status=TicketStatus.OPEN.value,
            category=category,
            created_by=created_by,
            created_at=datetime.now(timezone.utc),
        )
        return self.repository.create_ticket(ticket)

    def add_message(self, ticket_id: int,
                    message_text: str, author: str) -> TicketMessage:
        ticket = self.repository.get_ticket(ticket_id)
        if ticket is None:
            raise ValueError("ticket not found")
        message = TicketMessage(ticket_id=ticket_id,
                                message_text=message_text,
                                author=author)
        return self.repository.add_message(message)

    def update_status(self, ticket_id: int, status: str) -> Ticket:
        ticket = self.repository.get_ticket(ticket_id)
        if ticket is None:
            raise ValueError("ticket not found")
        ticket.status = status
        return self.repository.update_ticket(ticket)
