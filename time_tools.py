from datetime import datetime, time


def get_current_date():
    # Get the current date and time
    current_datetime = datetime.now()

    # Get the day of the week (0=Monday, 6=Sunday)
    day_of_week_numeric = current_datetime.weekday()

    return day_of_week_numeric


def get_seconds(hour, minute, seconds):
    # The target time you want to compare (e.g., 14:30:00 = 2:30 PM)
    target_time = time(hour=hour, minute=minute, second=seconds)  # Change this to your desired time

    # Get current time and combine it with today's date
    current_datetime = datetime.now()

    # Combine target_time with today's date
    target_datetime = datetime.combine(current_datetime.date(), target_time)
    pre_midnight = datetime.combine(current_datetime.date(), time(23, 59, 59))
    post_midnight = datetime.combine(current_datetime.date(), time(0, 0, 0))

    # Calculate the difference in seconds
    if pre_midnight >= current_datetime > target_datetime:
        time_diff = (pre_midnight - current_datetime) + (target_datetime - post_midnight)
    else:
        time_diff = target_datetime - current_datetime

    seconds_diff = time_diff.total_seconds()

    # print(f"Seconds between now and {target_time}: {seconds_diff}")
    return int(seconds_diff)
