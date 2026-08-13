
from flask import jsonify
from pydantic import ValidationError


def validation_error_response(exc: ValidationError, *,
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
