"""
Using geocode.xyz to retrieve lat, long from city and state.
This is a free service, but it has a limit of 1 request per second.
If you exceed this limit, you will receive a 403 error.
"""

# import http.client
import base64

import os
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
from repositories.geocode_repository import GeocodeRepository

load_dotenv()

try:
    from databricks.sdk import WorkspaceClient
except Exception:  # pragma: no cover - optional dependency in local runs
    WorkspaceClient = None


class GeopyRepository(GeocodeRepository):

    def __init__(self):
        self.app_name = os.environ.get('GEOPY_APP_NAME')
        if self.app_name:
            return
        scope = os.environ.get("LAKEBASE_SECRET_SCOPE", "database")
        geopy_app_name_key = os.environ.get("GEOPY_APP_SECRET_KEY",
                                            "geopy-app-name")
        workspace_client = (WorkspaceClient()
                            if WorkspaceClient is not None
                            else None)
        if workspace_client is not None:
            try:
                secret = workspace_client.secrets.get_secret(
                                            scope=scope,
                                            key=geopy_app_name_key)
                self.app_name = base64.b64decode(secret.value).decode("utf-8")
            except Exception:
                pass

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
        geolocator = Nominatim(user_agent=self.app_name)
        location = geolocator.geocode(f"{city}, {state_abbr}, USA")

        if location:
            return {"latitude": location.latitude,
                    "longitude": location.longitude}

        return {}
