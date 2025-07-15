from datetime import datetime, time


def get_current_date():
    # Get the current date and time
    current_datetime = datetime.now()

    # Extract the current time
    current_time = current_datetime.strftime("%H:%M:%S")

    # Get the day of the week (0=Monday, 6=Sunday)
    day_of_week_numeric = current_datetime.weekday()

    # Map the numeric day to a string representation
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_of_week_string = days[day_of_week_numeric]

    # print(f"Current Time: {current_time}")
    # print(f"Day of the Week: {day_of_week_string}")
    # print(f"Day of the week in number: {day_of_week_numeric}")
    return current_time, day_of_week_string, day_of_week_string


def get_seconds(hour, minute, seconds):
    # The target time you want to compare (e.g., 14:30:00 = 2:30 PM)
    target_time = time(hour=hour, minute=minute, second=seconds)  # Change this to your desired time

    # Get current time and combine it with today's date
    current_datetime = datetime.now()
    current_time = current_datetime.time()

    # Combine target_time with today's date
    target_datetime = datetime.combine(current_datetime.date(), target_time)

    # Calculate the difference in seconds
    if current_datetime > target_datetime:
        time_diff = current_datetime - target_datetime
    else:
        time_diff = target_datetime - current_datetime

    seconds_diff = time_diff.total_seconds()

    # print(f"Seconds between now and {target_time}: {seconds_diff}")
    return int(seconds_diff)


# print(get_seconds(9,30,0))
# print(get_current_date())