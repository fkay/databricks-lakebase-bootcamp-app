from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.weather_service import WeatherService
from repositories.city_repository import CityRepository
# from repositories.geocode_xyz_repository import GeocodeXYZRepository
from repositories.geopy_repository import GeopyRepository
from models.base import Base


@pytest.fixture
def service() -> WeatherService:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    city_repository = CityRepository(session_factory=SessionLocal)
    # geocode_repository = GeocodeXYZRepository()
    geocode_repository = GeopyRepository()
    return WeatherService(city_repository=city_repository,
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
