from __future__ import annotations

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from infrastructure.database import get_session_factory
from models.schemas import (TicketCreateRequest, TicketDetailResponse,
                            TicketMessageCreateRequest, TicketResponse,
                            TicketStatusUpdateRequest)
from repositories.ticket_repository import TicketRepository
from services.ticket_service import TicketService

bp = Blueprint("tickets", __name__)
service = TicketService(repository=TicketRepository(
                                    session_factory=get_session_factory()))


def _validation_error_response(exc: ValidationError, *,
                               error_type: str = "validation_error",
                               status_code: int = 422):
    details = []
    for error in exc.errors(include_url=False):
        loc = ".".join(str(part) for part in error.get("loc", ("body",)))
        details.append({
            "field": loc or "body",
            "message": error.get("msg", "Invalid value"),
        })

    return jsonify({
        "error": error_type,
        "details": details,
    }), status_code


@bp.route("/tickets", methods=["GET"])
def list_tickets():
    tickets = service.list_tickets()
    payload = [TicketResponse.model_validate(ticket).model_dump(mode="json")
               for ticket in tickets]
    return jsonify(payload)


@bp.route("/tickets", methods=["POST"])
def create_ticket():
    try:
        payload = TicketCreateRequest.model_validate(
                                request.get_json(silent=True) or {})
    except ValidationError as exc:
        return _validation_error_response(exc, status_code=422)

    ticket = service.create_ticket(title=payload.title,
                                   created_by=payload.created_by,
                                   category=payload.category)
    payload = TicketResponse.model_validate(ticket).model_dump(mode="json")
    return jsonify(payload), 201


@bp.route("/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id: int):
    ticket = service.get_ticket_with_messages(ticket_id)
    if ticket is None:
        return jsonify({"error": "ticket not found"}), 404
    payload = TicketDetailResponse.model_validate(ticket).model_dump(
                                                                mode="json")
    return jsonify(payload)


@bp.route("/tickets/<int:ticket_id>/messages", methods=["POST"])
def add_message(ticket_id: int):
    try:
        payload = TicketMessageCreateRequest.model_validate(
                                request.get_json(silent=True) or {})
    except ValidationError as exc:
        return _validation_error_response(exc, status_code=422)

    try:
        message = service.add_message(ticket_id,
                                      payload.message_text,
                                      payload.author)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404

    return jsonify({"id": message.message_id,
                    "content": message.message_text,
                    "author": message.author,
                    "created_at": message.created_at.isoformat()}), 201


@bp.route("/tickets/<int:ticket_id>/status", methods=["PATCH"])
def update_ticket_status(ticket_id: int):
    try:
        payload = TicketStatusUpdateRequest.model_validate(
                        request.get_json(silent=True) or {})
    except ValidationError as exc:
        return _validation_error_response(exc, status_code=422)

    try:
        ticket = service.update_status(ticket_id, payload.status)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404

    payload = TicketResponse.model_validate(ticket).model_dump(mode="json")
    return jsonify(payload)


@bp.route("/tickets/<int:ticket_id>/messages/<int:message_id>", methods=["DELETE"])
def delete_message(ticket_id: int, message_id: int):
    success = service.delete_message(message_id)
    if not success:
        return jsonify({"error": "message not found"}), 404
    return jsonify({"success": True}), 200
