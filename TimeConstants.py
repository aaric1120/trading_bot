import datetime as dt # Datetime is imported here, every script that imports this will have dateime as dt!!!!

MARKET_OPEN_TIME = dt.time(9, 45, 0)  # 9:45 AM (24-hour format) PARAM
MARKET_DEADLINE = dt.time(15, 30, 0)  # PARAM
LAST_MARKET_SELL = dt.time(15, 55, 0)
MARKET_CLOSE_TIME = dt.time(16, 0, 0)  # 4:00 PM (24-hour format) PARAM
PRE_MIDNIGHT = dt.time(23, 59, 59)
POST_MIDNIGHT = dt.time(0, 0, 0)
