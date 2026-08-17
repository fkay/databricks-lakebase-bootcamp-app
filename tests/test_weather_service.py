from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.city import City
from models.weather_doc import WeatherDoc
from services.weather_service import WeatherService
from repositories.db_weather_repository import DBWeatherRepository
# from repositories.geocode_xyz_repository import GeocodeXYZRepository
from repositories.geopy_repository import GeopyRepository
from models.base import Base


@pytest.fixture
def service() -> WeatherService:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    city_repository = DBWeatherRepository(session_factory=SessionLocal)
    # geocode_repository = GeocodeXYZRepository()
    geocode_repository = GeopyRepository()
    return WeatherService(db_weather_repository=city_repository,
                          geo_repository=geocode_repository)


def test_weather_lifecycle(service: WeatherService) -> None:
    city = service.create_city(
        name="Kansas City",
        state="Missouri",
        created_by="Ada",
    )

    assert city.name == "Kansas City"
    assert city.state == "MO"
    assert city.latitude is not None
    assert city.longitude is not None
    assert isinstance(city.latitude, Decimal)
    assert isinstance(city.longitude, Decimal)


def test_weather_get_city_forecast(service: WeatherService) -> None:
    test_city = City(
        name="Kansas City",
        state="MO",
        latitude=Decimal(39.1269),
        longitude=Decimal(-94.5866)
    )
    forecasts = service.get_forecast_city(test_city)

    assert len(forecasts) > 0
    assert isinstance(forecasts[0], WeatherDoc)


def test_weather_get_city_alert(service: WeatherService) -> None:
    test_city = City(
        name="Kansas City",
        state="MO",
        latitude=Decimal(39.1269),
        longitude=Decimal(-94.5866)
    )
    alerts = service.get_alert_city(test_city)

    assert len(alerts) >= 0
