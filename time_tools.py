import time as tm
from TimeConstants import *


def get_current_date():
    # Get the current date and time
    current_datetime = dt.datetime.now()

    # Get the day of the week (0=Monday, 6=Sunday)
    day_of_week_numeric = current_datetime.weekday()

    return day_of_week_numeric


def get_seconds(hour, minute, seconds):
    """
    Get the seconds between 2 specified time...
    :param hour:
    :param minute:
    :param seconds:
    :return:
    """
    # The target time you want to compare (e.g., 14:30:00 = 2:30 PM)
    target_time = dt.time(hour=hour, minute=minute, second=seconds)  # Change this to your desired time

    # Get current time and combine it with today's date
    current_datetime = dt.datetime.now()

    # Combine target_time with today's date
    target_datetime = dt.datetime.combine(current_datetime.date(), target_time)
    pre_midnight = dt.datetime.combine(current_datetime.date(), dt.time(23, 59, 59))
    post_midnight = dt.datetime.combine(current_datetime.date(), dt.time(0, 0, 0))

    # Calculate the difference in seconds
    if pre_midnight >= current_datetime > target_datetime:
        time_diff = (pre_midnight - current_datetime) + (target_datetime - post_midnight)
    else:
        time_diff = target_datetime - current_datetime

    seconds_diff = time_diff.total_seconds()

    # print(f"Seconds between now and {target_time}: {seconds_diff}")
    return int(seconds_diff)


def sleep_til_market():
    """
    check if the time is ready...
    :return:
    """
    # # Check if market is open or not...
    # MARKET_OPEN_TIME = dt.time(9, 45, 0)  # 9:45 AM (24-hour format) PARAM
    # MARKET_CLOSE_TIME = dt.time(16, 0, 0)  # 4:00 PM (24-hour format) PARAM
    # MARKET_DEADLINE = dt.time(15, 30, 0)  # PARAM
    # PRE_MIDNIGHT = dt.time(23, 59, 59)
    # POST_MIDNIGHT = dt.time(0, 0, 0)
    CURR_DAY = get_current_date()

    if (MARKET_CLOSE_TIME < dt.datetime.now().time() < PRE_MIDNIGHT
        or POST_MIDNIGHT < dt.datetime.now().time() < MARKET_OPEN_TIME) or CURR_DAY >= 5:
        print("The Market hasn't opened yet...")
        sleep_sec = get_seconds(9, 45, 0)  # PARAM

        # Checks the day of the week to calculate the time to wait
        if (CURR_DAY == 4 and MARKET_CLOSE_TIME < dt.datetime.now().time() < PRE_MIDNIGHT):
            sleep_sec += 86400 * 2
        elif CURR_DAY == 5:
            if dt.datetime.now().time() < MARKET_OPEN_TIME:
                sleep_sec += 86400 * 2
            else:
                sleep_sec += 86400 * 1.5
        elif CURR_DAY == 6:
            if dt.datetime.now().time() < MARKET_OPEN_TIME:
                sleep_sec += 86400
            else:
                sleep_sec += 86400 * 0.5

        print(f"Sleeping for {int(sleep_sec / 3600)} Hours "
              f"and {int((sleep_sec % 3600) / 60)} Minutes until Marktet opens...")
        tm.sleep(sleep_sec)
