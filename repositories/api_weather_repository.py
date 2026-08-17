from decimal import Decimal
from functools import lru_cache

import requests
import json


class APIWeatherRepository():

    def __init__(self):
        self.api_url = 'https://api.weather.gov'

    @lru_cache(maxsize=128)
    def get_point(self, latitude: Decimal, longitude: Decimal) -> dict:
        """
        Get point information from api.weather.gov

        Args:
            latitude (Decimal): latitude
            longitude (Decimal): longitude

        Returns:
            dict: forecast_url, grid_x, grid_y, wfo
        """

        with requests.Session() as session:
            session.headers = {"Accept": "application/json"}
            url = self.api_url + f"/points/{latitude},{longitude}"
            response = session.get(url)

        if response.status_code != 200:
            return {}

        result = json.loads(response.text.encode('utf-8'))

        props = result.get("properties")
        forecast_url = props.get("forecast")
        grid_x = props.get("gridX")
        grid_y = props.get("gridY")
        wfo = props.get("gridId")
        zone = props.get("forecastZone", "").split("/")[-1]

        return {"forecast_url": forecast_url,
                "wfo": wfo,
                "grid_x": grid_x,
                "grid_y": grid_y,
                "zone": zone}

    def get_forecast(self, wfo: str, grid_x: int, grid_y: int) -> list[dict]:
        url = self.api_url + f"/gridpoints/{wfo}/{grid_x},{grid_y}/forecast"

        with requests.Session() as session:
            session.headers = {"Accept": "application/json"}
            response = session.get(url)

        if response.status_code != 200:
            return []

        result = json.loads(response.text.encode('utf-8'))

        periods = result.get("properties").get("periods")
        forecasts = []
        for period in periods:
            name = period.get("name")
            detailed_forecast = period.get("detailedForecast")
            start = period.get("startTime")
            end = period.get("endTime")
            forecasts.append({"name": name,
                              "forecast": detailed_forecast,
                              "start_time": start,
                              "end_time": end,
                              "payload": period})
        return forecasts

    def get_alerts(self, latitude: Decimal, longitude: Decimal) -> list[dict]:
        url = self.api_url + "/alerts/active"
        params = {
            "point": f"{latitude}, {longitude}"
        }
        with requests.Session() as session:
            session.headers = {"Accept": "application/json"}
            response = session.get(url, params=params)

        if response.status_code != 200:
            return []

        result = json.loads(response.text.encode('utf-8'))

        features = result.get("features")
        alerts = []
        for feat in features:
            id = feat.get("id")
            effective_at = feat.get("effective")
            headline = feat.get("headline")
            description = feat.get("description")
            instruction = feat.get("instruction")
            alerts.append({
                "id": id,
                "effective_at": effective_at,
                "headline": headline,
                "description": description,
                "instruction": instruction,
                "payload": feat
            })

        return alerts
