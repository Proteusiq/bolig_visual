"""
FlightAware API
Create a Python API to get flight Data from FlightAware
By Prayson W. Daniel
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict
from requests import Session
import json


class Aviation(ABC):

    """
        The abstract class to which flight(s) classes will be built on by
        overiding get method
    """

    def __init__(self, headers=None):

        self.flight_url = "https://flightaware.com/ajax/trackpoll.rvt"
        self.flights_url = "https://flightaware.com/ajax/vicinity_aircraft.rvt"
        self.main_url = "https://flightaware.com/live/"

        session = Session()

        if headers is None:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/39.0.2171.95 Safari/537.36"
                ),
            }

        session.headers.update(headers)
        self.session = session

    @abstractmethod
    def get(self, *args, **kwargs):
        pass


class Flight(Aviation):
    """Get Flight Information 
    """

    def get(self, icao_id: str) -> Dict:
        """
          Requires Flight ICAO ID
          Raises ConnectionError when token not found.
          Returns Dictionary of Flight Information
        """

        url = f"{self.main_url}flight/{icao_id}"
        response = self.session.get(url)

        if response.ok:

            start = response.text.find("trackpollGlobals") + 19
            end = response.text.find("USERTOKEN") + 23

            self.token = json.loads(response.text[start:end]).get("TOKEN")

        else:
            raise ConnectionError("No token found!")

        print(f"[INFO] ICAO: {icao_id} | Token: {self.token}")

        params = dict(token=self.token, locale="en_US", summary=1)

        json_response = self.session.get(self.flight_url, params=params)

        return json_response.json()


class Flights(Aviation):
    """Get Flights Information 
    """

    def get(self) -> Dict:
        """
        Returns Dictionary of Flights Information
        Raises ConnectionError when token not found.
        """

        response = self.session.get(self.main_url)

        if response.ok:

            start = response.text.find("mapGlobals") + 13
            end = start + response.text[start:].find("</script>") - 1

            self.token = json.loads(response.text[start:end]).get("VICINITY_TOKEN")

        else:
            raise ConnectionError("No token found!")

        print(f"[INFO] Token: {self.token}")

        params = dict(
            minLon=-180,
            minLat=31.95648193359375,
            maxLon=-102.28792905807495,
            maxLat=36.9140625,
            token=self.token,
        )

        json_response = self.session.get(self.flights_url, params=params)

        return json_response.json()
