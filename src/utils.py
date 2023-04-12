import math
from datetime import datetime, timedelta
import time


class UserFuckUpException(Exception):
    pass

def fetch_event_id_from_url(url: str) -> str:
    addr_stripped = url.lstrip("https://tihlde.org/arrangementer/")
    num, _ = addr_stripped.split("/",1)
    return num



def get_timedelta_as_components(delta: timedelta) -> (int, int, int, int):
    delta_days = delta.days
    days_rest = (delta.total_seconds() - (delta_days * 60 * 60 * 24))
    delta_hours = math.floor(days_rest / (60 * 60))
    hours_rest = days_rest - (delta_hours * 60 * 60)
    delta_minutes = math.floor(hours_rest / 60)
    minutes_rest = hours_rest - delta_minutes * 60
    delta_seconds = math.floor(minutes_rest)
    return (delta_days, delta_hours, delta_minutes, delta_seconds)


def wait_until_dt(dt: datetime, verbose):
    now = datetime.now(dt.tzinfo)
    delta = dt - now

    if verbose:
        days, hours, minutes,seconds = get_timedelta_as_components(delta)
        delta_string = f"The system will wake in {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds"
        print(delta_string)

    sleep_time = delta.total_seconds() + delta.microseconds / 1e6

    sleep_time = max(sleep_time, 0)
    time.sleep(sleep_time)
