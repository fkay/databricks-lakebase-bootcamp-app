from datetime import datetime, timezone
from models.city import City
from repositories.city_repository import CityRepository
from repositories.reverse_geocode_repository import ReverseGeocodeRepository


class WeatherService:
    def __init__(self, city_repository: CityRepository,
                 rev_geo_repository: ReverseGeocodeRepository) -> None:
        self.city_repository = city_repository
        self.rev_geo_repository = rev_geo_repository

    def list_cities(self) -> list[City]:
        return self.city_repository.list_cities()

    def list_states(self) -> list[str]:
        return self.rev_geo_repository.get_state_list()

    def get_city(self, city_id: int) -> City | None:
        return self.city_repository.get_city(city_id)

    def create_city(self, name: str, state: str,
                    created_by: str) -> City:
        # get lat and long
        geocode = self.rev_geo_repository.get_lat_long(city=name, state=state)
        abbr_state = ReverseGeocodeRepository.get_abbr_state(state)
        return self.insert_city(name, abbr_state,
                                geocode.get("latitude"),
                                geocode.get("longitude"),
                                created_by)

    def insert_city(self, name: str, state: str,
                    latitude: float, longitude: float,
                    created_by: str) -> City:
        city = City(
            name=name,
            state=state,
            created_by=created_by,
            latitude=latitude,
            longitude=longitude,
            created_at=datetime.now(timezone.utc),
        )
        return self.city_repository.create_city(city)

    def delete_city(self, city_id: int) -> bool:
        return self.city_repository.delete_city(city_id)
