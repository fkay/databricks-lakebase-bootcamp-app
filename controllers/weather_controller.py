from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from repositories.db_weather_repository import DBWeatherRepository
from repositories.geopy_repository import GeopyRepository
from models.schemas import (CityListRequest, CityResponse, CityCreateRequest)
from services.weather_service import WeatherService
from infrastructure.database import get_session_factory
from controllers.validation_error_response import validation_error_response

bp = Blueprint("weather", __name__)
service = WeatherService(
    db_weather_repository=DBWeatherRepository(
                    session_factory=get_session_factory()),
    geo_repository=GeopyRepository()
    )


@bp.route("/weather/cities", methods=["GET"])
def list_tickets():
    cities = service.list_cities()
    cities.sort(key=lambda city: city.name)
    payload = [CityResponse.model_validate(city).model_dump(mode="json")
               for city in cities]
    return jsonify(payload)


@bp.route("/weather/states", methods=["GET"])
def list_states():
    states = service.list_states()
    return jsonify(states)


@bp.route("/weather/cities", methods=["POST"])
def create_city():
    try:
        payload = CityCreateRequest.model_validate(
                                request.get_json(silent=True) or {})
    except ValidationError as exc:
        return validation_error_response(exc, status_code=422)

    city = service.create_city(name=payload.name,
                               state=payload.state,
                               created_by=payload.created_by)
    payload = CityResponse.model_validate(city).model_dump(mode="json")
    return jsonify(payload), 201


@bp.route("/weather/cities/<int:city_id>",
          methods=["DELETE"])
def delete_city(city_id: int):
    success = service.delete_city(city_id)
    if not success:
        return jsonify({"error": "city not found"}), 404
    return jsonify({"success": True}), 200


@bp.route("/weather/sync", methods=["POST"])
def sync_weather_docs():
    try:
        payload = CityListRequest.model_validate(
            request.get_json(silent=True) or {}
        )
    except ValidationError as exc:
        return validation_error_response(exc, status_code=422)

    synced_docs = service.sync_weather_docs(payload.city_list)
    return jsonify({"Docs synced": synced_docs}), 200
