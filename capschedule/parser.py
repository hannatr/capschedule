import calendar
import datetime
import json

import pandas as pd

# JSON fields
START = "start"
END = "end"
HOLIDAYS = "holidays"  # used twice
STAFF = "staff"
NAME = "name"
ASSIGNMENTS = "assignments"
DATES_OFF = "dates-off"


def load():
    """
    Loads a JSON config file, creates a schedule, and populates black out dates
    :return: Tuple of the schedule and populated staff dictionary
    """
    config = json.load(open(f"../config/2021.json", "r"))

    config[START] = datetime.datetime.strptime(config[START], "%Y-%m-%d")
    config[END] = datetime.datetime.strptime(config[END], "%Y-%m-%d")
    delta = (config[END] - config[START]).days + 1
    year = config[START].year

    # Schedule is a list of months with two time slots per day
    schedule = []
    for i in range(config[START].month, config[END].month):
        days_in_month = calendar.monthrange(year, i)[1]
        schedule.append(
            pd.Series(
                [None] * days_in_month * 2,
                index=pd.date_range(
                    datetime.datetime(year, i, 1, 7, 0),
                    freq="12H",
                    periods=days_in_month * 2,
                ),
            )
        )
    master = pd.Series(
        [None] * delta * 2,
        index=pd.date_range(
            datetime.datetime.combine(config[START], datetime.time(7, 0)),
            freq="12H",
            periods=delta * 2,
        ),
    )

    # Parse and then set each staff member's black out dates
    staff_list = config[STAFF]
    for person in staff_list:
        blackout = []
        for t in person[DATES_OFF]:
            if t["compare"] == "in":
                for key, value in master.items():
                    if getattr(key, t["prop"]) in t["value"] and str(key).endswith(
                        t["time"]
                    ):
                        blackout.append(key)
            elif t["compare"] == "equals":
                for key, value in master.items():
                    if str(key) in t["value"]:
                        blackout.append(key)
            elif t["compare"] == "nth":
                month = master.keys()[0].month
                count = 1
                for key, value in master.items():
                    if key.month != month:
                        count = 1
                        month = key.month

                    if key.dayofweek == t["day"]:
                        if count == t["count"]:
                            if str(key).endswith(t["time"]):
                                blackout.append(key)
                        if str(key).endswith("19:00:00"):
                            count += 1
        person[DATES_OFF] = blackout
    config[STAFF] = staff_list

    return schedule, config
