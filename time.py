from datetime import datetime


# Get the current date and time
current_datetime = datetime.now()

# Extract the current time
current_time = current_datetime.strftime("%H:%M:%S")

# Get the day of the week (0=Monday, 6=Sunday)
day_of_week_numeric = current_datetime.weekday()

# Map the numeric day to a string representation
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_of_week_string = days[day_of_week_numeric]

print(f"Current Time: {current_time}")
print(f"Day of the Week: {day_of_week_string}")
print(f"Day of the week in number: {day_of_week_numeric}")
