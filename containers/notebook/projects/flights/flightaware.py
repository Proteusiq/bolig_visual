"""
FlightAware API
Create a Python API to get flight Data from FlightAware
By Prayson W. Daniel
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import json
from typing import Dict, List, Optional
from joblib import Parallel, delayed, parallel_backend
from requests import Session


class Aviation(ABC):

    """
        The abstract class to which flight(s) classes will be built on by
        overiding get method
    """

    def __init__(self, headers: Optional[Dict] = None) -> None:

        self.flight_url = "https://flightaware.com/ajax/trackpoll.rvt"
        self.flights_url = "https://flightaware.com/ajax/vicinity_aircraft.rvt"
        self.main_url = "https://flightaware.com/live/"
        self.token = None

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

    def get(self, icao_id: str, verbose: Optional[bool] = False) -> Dict:
        """
          Requires Flight ICAO ID
          Raises ConnectionError when token not found.
          Returns Dictionary of Flight Information
        """

        if not self.token:
            url = f"{self.main_url}flight/{icao_id}"
            response = self.session.get(url)

            if response.ok:

                start = response.text.find("trackpollGlobals") + 19
                end = response.text.find("USERTOKEN") + 23

                self.token = json.loads(response.text[start:end]).get("TOKEN")

            else:
                raise ConnectionError("No token found!")

        if verbose:
            print(f"[INFO] ICAO: {icao_id} | Token: {self.token}")

        params = dict(token=self.token, locale="en_US", summary=1)

        json_response = self.session.get(self.flight_url, params=params)

        return json_response.json()


class Flights(Aviation):
    """Get Flights Information 
    """

    def get(
        self, params: Optional[Dict] = None, verbose: Optional[bool] = False
    ) -> List[Dict]:
        """
        Returns Dictionary of Flights Information
        Raises ConnectionError when token not found.
        """

        if not self.token:
            response = self.session.get(self.main_url)

            if response.ok:

                start = response.text.find("mapGlobals") + 13
                end = start + response.text[start:].find("</script>") - 1

                self.token = json.loads(response.text[start:end]).get("VICINITY_TOKEN")

            else:
                raise ConnectionError("No token found!")

        if verbose:
            print(f"[INFO] Token: {self.token}")

        if params is None:

            with open(f"{Path(__file__).parent}/geolocation.json", "r") as f:
                geolocation = json.load(f)

            # update geolocation with token
            {location.update({"token": self.token}) for location in geolocation}

            # run using joblib multithreading
            with parallel_backend("threading", n_jobs=14):
                json_responses = Parallel()(
                    delayed(
                        lambda url, param: self.session.get(url, params=param).json()
                    )(self.flights_url, param)
                    for param in geolocation
                )

            return json_responses

        # if params are given, update token
        params.update({"token": self.token})

        return [self.session.get(self.flights_url, params=params).json()]
