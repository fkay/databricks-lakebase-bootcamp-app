import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.ticket_service import TicketService
from repositories.ticket_repository import TicketRepository
from models.base import Base


@pytest.fixture
def service() -> TicketService:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    repository = TicketRepository(session_factory=SessionLocal)
    return TicketService(repository=repository)


def test_ticket_lifecycle(service: TicketService) -> None:
    ticket = service.create_ticket(
        title="Printer not working",
        created_by="Ada",
        category="hardware",
    )

    assert ticket.status == "open"
    assert ticket.category == "hardware"

    service.add_message(ticket.ticket_id, "I can help with that.", "support")
    service.update_status(ticket.ticket_id, "in_progress")

    loaded = service.get_ticket_with_messages(ticket.ticket_id)
    assert loaded.title == "Printer not working"
    assert loaded.status == "in_progress"
    assert loaded.category == "hardware"
    assert len(loaded.messages) == 1
    assert loaded.messages[0].message_text == "I can help with that."
