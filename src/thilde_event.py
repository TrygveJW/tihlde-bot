import math
import time

import requests
import datetime

from utils import get_timedelta_as_components


def _parse_datetime(dt_string: str) -> datetime.datetime:
    pattern = "%Y-%m-%dT%H:%M:%S%z"
    out = datetime.datetime.strptime(dt_string, pattern)
    return out


class ThildeEvent:
    _event_api_endpoint_blank = "https://api.tihlde.org/events/{}/"

    def __init__(self, event_id: int):
        event_url = self._event_api_endpoint_blank.format(event_id)
        response = requests.get(event_url)

        if response.status_code != 200:
            raise Exception("invalid event url")

        response_json = response.json()
        # print(response_json)
        self.id = int(response_json["id"])
        self.title = response_json["title"]
        self.event_start = _parse_datetime(response_json["start_date"])
        self.registration_start = _parse_datetime(response_json["start_registration_at"])
        self.registration_end = _parse_datetime(response_json["end_registration_at"])

    def display_event(self):
        print(f"The selected event is {self.id} with title: {self.title}")
        delta = self.get_timedelta_to_reg_start()
        days, hours, minutes,seconds = get_timedelta_as_components(delta)

        delta_string = f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds"
        print(f"The registration start time is {self.registration_start} which is in {delta_string}")

    def get_timedelta_to_reg_start(self) -> datetime.timedelta:
        return self.registration_start - datetime.datetime.now(self.registration_start.tzinfo)
