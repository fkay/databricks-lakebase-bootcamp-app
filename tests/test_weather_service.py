import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.weather_service import WeatherService
from repositories.city_repository import CityRepository
from repositories.reverse_geocode_repository import ReverseGeocodeRepository
from models.base import Base


@pytest.fixture
def service() -> WeatherService:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    city_repository = CityRepository(session_factory=SessionLocal)
    reverse_geocode_repository = ReverseGeocodeRepository()
    return WeatherService(city_repository=city_repository,
                          rev_geo_repository=reverse_geocode_repository)


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
    assert isinstance(city.latitude, float)
    assert isinstance(city.longitude, float)
