import datetime
import os
from zoneinfo import ZoneInfo

import flask
import functions_framework
from nyct_gtfs import NYCTFeed

API_KEY = os.getenv("MTA_API_KEY")
STOP_ID = "A31N"  # A31N is 14th
NEW_YORK = ZoneInfo("America/New_York")


@functions_framework.http
def train_schedule_get(request: flask.Request):
    print("Getting MTA data")
    upcoming_train_times = get_upcoming_train_times()
    print("Done getting MTA data")
    return build_response(upcoming_train_times)


def get_upcoming_train_times() -> list[tuple[datetime.datetime, bool]]:
    feed = NYCTFeed("E", api_key=API_KEY)
    trains = feed.filter_trips(line_id=["E"], headed_for_stop_id=[STOP_ID])
    upcoming_train_times = []
    for train in trains:
        for stop_update in train.stop_time_updates:
            if stop_update.stop_id == STOP_ID:
                upcoming_train_times.append((stop_update.arrival, train.underway))
                break
    upcoming_train_times = sorted(
        upcoming_train_times, key=lambda train_time: (train_time[0], not train_time[1])
    )
    return upcoming_train_times


def build_response(upcoming_train_times: list[tuple[datetime.datetime, bool]]) -> str:
    train_time_strs = []
    for upcoming_train_time in upcoming_train_times:
        stop_time, underway = upcoming_train_time
        stop_time = stop_time.astimezone(NEW_YORK)
        train_time_strs.append(
            f"{stop_time.strftime('%X')} ({'underway' if underway else 'scheduled'})"
        )

    message = (
        f'The next Uptown E trains from 14th St are: {", ".join(train_time_strs)}.'
    )

    return message
