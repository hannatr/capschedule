import copy
import random

from capschedule.parser import (ASSIGNMENTS, DATES_OFF, HOLIDAYS, NAME, STAFF,
                                load)

previous = None
holiday_list = ()


def is_holiday(date):
    """
    Determines if a date is considered a holiday
    :param date: Date to check
    :return: True if holiday, False otherwise
    """
    global holiday_list

    return (
        date.dayofweek in [5, 6]
        or (date.dayofweek == 4 and str(date).endswith("19:00:00"))
        or str(date).startswith(holiday_list)
    )


def get_next(staff, idx, date):
    """
    Find a suitable staff member to fill this time slot
    :param staff: Master list of staff data
    :param idx: Month index for assignments
    :param date: Time slot to fill
    :return: Name of candidate that can fill this time slot
    :raises: LookupError if not suitable candidate found
    """
    global previous

    random.shuffle(staff)
    for candidate in staff:
        if (
            candidate[ASSIGNMENTS][idx] > 0
            and date not in candidate[DATES_OFF]
            and candidate[NAME] != previous
        ):
            if is_holiday(date):
                if candidate[HOLIDAYS][idx] > 0:
                    candidate[HOLIDAYS][idx] -= 1
                else:
                    continue
            elif candidate[ASSIGNMENTS][idx] == candidate[HOLIDAYS][idx]:
                continue  # If person has only holidays left, don't assign them a non-holiday

            candidate[ASSIGNMENTS][idx] -= 1
            return candidate
    raise LookupError(f"Could not find a suitable candidate for time {date}")


def main():
    """
    Calculates the schedule, prints it out
    """
    global previous, holiday_list

    # load the config file
    schedule, config = load()
    staff_list = config[STAFF]
    holiday_list = tuple(config[HOLIDAYS])

    # try until we get a combo that meets criteria
    i = 0
    while True:
        previous = None
        i += 1
        if i % 1000 == 0:
            print(i)
        try:
            temp = copy.deepcopy(staff_list)
            # divide into month blocks, fill out one month at a time
            for idx, month in enumerate(schedule):
                for slot in month.keys():
                    s = get_next(temp, idx, slot)
                    month[slot] = s[NAME]
                    previous = s[NAME]
                break  # TODO remove
            break  # we did it, break out of loop
        except LookupError:
            continue

    for index, value in list(schedule[0].items()):
        print(f"{index} {value}")
