from TimeConstants import *

from time_tools import sleep_til_market
from stock_screener import get_stock_start

import time as tm


def main():
    while True:
        # Sleep til market opens
        sleep_til_market()

        # variables that track the process
        stock_list = []
        stock_dict = set()
        process_list = []

        # Main loop to add new stocks every 15 minutes...
        while True:
            # Check close time for market
            if dt.datetime.now().time() >= MARKET_CLOSE_TIME:
                print("The Market has closed...")
                return
            else:
                # Check if the process has finished
                for i in range(len(stock_list)):
                    if (stock_list[i] is not None):
                        if process_list[i].poll() is not None:
                            stock_dict.remove(stock_list[i])
                            stock_list[i] = None

                # Don't get new stock after deadline
                if dt.datetime.now().time() <= MARKET_DEADLINE:
                    # Get new stocks to add...
                    print("Adding new stocks to the list...")
                    get_stock_start(stock_list, stock_dict, process_list)
                    print(f"The Current active stocks are {stock_dict}")

                # Exit the loop if past market deadline
                elif dt.datetime.now().time() > MARKET_DEADLINE:
                    break

                print("Sleeping for 15 minutes until next stock check...")
                tm.sleep(900)  # PARAM


if __name__ == "__main__":
    main()