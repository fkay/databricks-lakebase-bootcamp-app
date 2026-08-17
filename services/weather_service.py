from datetime import datetime, timezone
import json
from time import sleep
from models.city import City
from models.weather_doc import WeatherDoc, WeatherSourceType
from repositories.db_weather_repository import DBWeatherRepository
from repositories.geocode_repository import GeocodeRepository
from repositories.api_weather_repository import APIWeatherRepository


class WeatherService:
    def __init__(self, db_weather_repository: DBWeatherRepository,
                 geo_repository: GeocodeRepository) -> None:
        self.db_weather_repository = db_weather_repository
        self.rev_geo_repository = geo_repository
        self.api_weather_repository = APIWeatherRepository()

    def list_cities(self) -> list[City]:
        return self.db_weather_repository.list_cities()

    def list_states(self) -> list[str]:
        return self.rev_geo_repository.get_state_list()

    def get_city(self, city_id: int) -> City | None:
        return self.db_weather_repository.get_city(city_id)

    def create_city(self, name: str, state: str,
                    created_by: str) -> City:
        # get lat and long
        geocode = self.rev_geo_repository.get_lat_long(city=name, state=state)
        abbr_state = GeocodeRepository.get_abbr_state(state)
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
        return self.db_weather_repository.create_city(city)

    def delete_city(self, city_id: int) -> bool:
        return self.db_weather_repository.delete_city(city_id)

    def get_forecast_city(self, city: City) -> list[WeatherDoc]:
        loc = self.api_weather_repository.get_point(city.latitude,
                                                    city.longitude)
        forecasts = self.api_weather_repository.get_forecast(
                                                    loc["wfo"],
                                                    loc["grid_x"],
                                                    loc["grid_y"])
        final_result = []
        for forecast in forecasts:
            weather_doc = WeatherDoc(
                weather_id=(f"{city.name}:{city.state}"
                            f":{forecast['start_time']}"),
                location=f"{city.name}-{city.state}",
                source_type=WeatherSourceType.FORECAST,
                headline=forecast["forecast"],
                narrative_text=forecast["forecast"],
                event_date=datetime.fromisoformat(forecast["start_time"]),
                payload=json.dumps(forecast["payload"])
            )
            final_result.append(weather_doc)
        return final_result

    def get_alert_city(self, city: City) -> list[WeatherDoc]:
        alerts = self.api_weather_repository.get_alerts(city.latitude,
                                                        city.longitude)
        final_result = []
        for alert in alerts:
            weather_doc = WeatherDoc(
                weather_id=alert["id"],
                location=f"{city.name}-{city.state}",
                source_type=WeatherSourceType.ALERT,
                headline=alert["headline"],
                narrative_text=(f"Description: {alert['description']};"
                                f"Instructions: {alert['instruction']}"),
                event_date=datetime.fromisoformat(alert["effective_at"]),
                payload=json.dumps(alert["payload"])
            )
            final_result.append(weather_doc)
        return final_result

    def sync_weather_docs(self, cities: list[dict[str, str]] | None) -> int:
        if cities is None or len(cities) == 0:
            cities_adm = self.list_cities()
        else:
            cities_adm = []
            for city in cities:
                geocode = self.rev_geo_repository.get_lat_long(
                                                    city=city.name,
                                                    state=city.state)
                abbr_state = GeocodeRepository.get_abbr_state(city.state)
                cities_adm.append(City(
                                name=city.name,
                                state=abbr_state,
                                created_by="internal",
                                latitude=geocode.get("latitude"),
                                longitude=geocode.get("longitude"),
                                created_at=datetime.now(timezone.utc),
                ))
        docs_synced = 0
        for city in cities_adm:
            for weather_doc in self.get_forecast_city(city):
                self.db_weather_repository.add_weather_doc(weather_doc)
                docs_synced += 1
                sleep(1000)     # maintain api on rate limit
            for weather_doc in self.get_alert_city(city):
                self.db_weather_repository.add_weather_doc(weather_doc)
                docs_synced += 1
                sleep(1000)     # maintain api on rate limit
        return docs_synced
