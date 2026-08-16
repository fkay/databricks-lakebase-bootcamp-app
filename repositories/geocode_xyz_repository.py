"""
Using geocode.xyz to retrieve lat, long from city and state.
This is a free service, but it has a limit of 1 request per second.
If you exceed this limit, you will receive a 403 error.
"""

# import http.client
import base64

import requests
import os
import json
from dotenv import load_dotenv

from repositories.geocode_repository import GeocodeRepository

load_dotenv()

try:
    from databricks.sdk import WorkspaceClient
except Exception:  # pragma: no cover - optional dependency in local runs
    WorkspaceClient = None


class GeocodeXYZRepository(GeocodeRepository):

    def __init__(self):
        self.api_url = 'https://geocode.xyz'
        self.api_key = os.environ.get('GEOCODE_XYZ_API_KEY')
        if self.api_key:
            return
        scope = os.environ.get("LAKEBASE_SECRET_SCOPE", "database")
        geocode_xyz_secret_key = os.environ.get("GEOCODE_XYZ_SECRET_KEY",
                                                "geocode-xyz-api-key")
        workspace_client = (WorkspaceClient()
                            if WorkspaceClient is not None
                            else None)
        if workspace_client is not None:
            try:
                secret = workspace_client.secrets.get_secret(
                                            scope=scope,
                                            key=geocode_xyz_secret_key)
                self.api_key = base64.b64decode(secret.value).decode("utf-8")
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
