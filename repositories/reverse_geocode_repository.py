"""
Using geocode.xyz to retrieve lat, long from city and state.
This is a free service, but it has a limit of 1 request per second.
If you exceed this limit, you will receive a 403 error.
"""

# import http.client
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()


class ReverseGeocodeRepository:

    _us_states_to_abbr = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
        "California": "CA", "Colorado": "CO", "Connecticut": "CT",
        "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
        "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN",
        "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
        "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
        "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
        "Missouri": "MO", "New Hampshire": "NH",
        "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
        "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
        "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
        "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
        "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
        "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
        "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
        "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC"
    }

    def __init__(self):
        self.api_url = 'https://geocode.xyz'
        self.api_key = os.environ.get('GEOCODE_XYZ_API_KEY')

    @classmethod
    def get_abbr_state(cls, state: str) -> str:
        return (state if len(state) == 2
                else cls._us_states_to_abbr.get(state))

    @classmethod
    def get_state_list(cls) -> list[str]:
        return [f"{k}-{v}" for k, v in cls._us_states_to_abbr.items()]

    def get_lat_long(self, city: str, state: str) -> dict:
        """
        Get lat, long from geocode.xyz based on city name and state.
        If state name length more than 2 chars, get the abbreviation from
        dict.

        Args:
            city (str): city name
            state (str): state name or state abbreviation

        Returns:
            dict: latitude (float), longitude (float)
                  or empty dict if not found
        """
        state_abbr = self.get_abbr_state(state)

        with requests.Session() as session:
            params = {
                'auth': self.api_key,
                'locate': f"{city}, {state_abbr}",
                'region': 'NorthAmerica',
                'json': 1,
                }

            response = session.get(self.api_url, params=params)

        if response.status_code != 200:
            return {}

        result = json.loads(response.text.encode('utf-8'))

        lat = float(result.get("latt"))
        long = float(result.get("longt"))

        return {"latitude": lat, "longitude": long} if lat and long else {}
