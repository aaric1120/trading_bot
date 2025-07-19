from time_tools import get_current_date, get_seconds
from stock_screener import get_stock_start

import datetime as dt
import time as tm


def main():
    # Check if market is open or not...
    MARKET_OPEN_TIME = dt.time(9, 45, 0)  # 9:45 AM (24-hour format) PARAM
    MARKET_CLOSE_TIME = dt.time(16, 0, 0)  # 4:00 PM (24-hour format) PARAM
    MARKET_DEADLINE = dt.time(15,30,0) # PARAM
    PRE_MIDNIGHT = dt.time(23, 59, 59)
    POST_MIDNIGHT = dt.time(0, 0, 0)
    CURR_DAY = get_current_date()

    while True:
        if MARKET_CLOSE_TIME < dt.datetime.now().time() < PRE_MIDNIGHT \
                or POST_MIDNIGHT < dt.datetime.now().time() < MARKET_OPEN_TIME:
            print("The Market hasn't opened yet...")
            sleep_sec = get_seconds(9,45,0) # PARAM

            # Checks the day of the week to calculate the time to wait
            if (CURR_DAY == 4 and MARKET_CLOSE_TIME < dt.datetime.now().time() < PRE_MIDNIGHT) or CURR_DAY > 4:
                sleep_sec += 86400 * (6 - CURR_DAY)

            print(f"Sleeping for {int(sleep_sec/3600)} Hours "
                  f"and {int((sleep_sec % 3600) / 60)} Minutes until Marktet opens...")
            tm.sleep(sleep_sec)

        # variables that track the process
        stock_list = []
        stock_dict = set()
        process_list = []

        # Main loop to add new stocks every 15 minutes...
        while True:
            # Check close time for market
            if dt.datetime.now().time() > MARKET_CLOSE_TIME:
                print("The Market has closed...")
                break
            else:
                # Check if the process has finished
                for i in range(len(stock_list)):
                    if (stock_list[i] is not None):
                        if process_list[i].poll() is not None:
                            stock_dict.remove(stock_list[i])
                            stock_list[i] = None

                # Don't get new stock after deadline
                if dt.datetime.now().time() < MARKET_DEADLINE:
                    # Get new stocks to add...
                    print("Adding new stocks to the list...")
                    get_stock_start(stock_list, stock_dict, process_list)
                    print(f"The Current active stocks are {stock_dict}")

                print("Sleeping for 15 minutes until next stock check...")
                tm.sleep(900)  # PARAM


if __name__ == "__main__":
    main()