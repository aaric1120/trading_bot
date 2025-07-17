from time_tools import get_current_date, get_seconds
import datetime as dt
import time as tm

from stock_screener import get_undervalued_stocks
import subprocess


def get_stock_start(stock_list,stock_dict,process_list):
    # get list of stocks available for trading
    watch_list = get_undervalued_stocks()

    # print(f"Current list of available stockes to trade: {watch_list}")

    if (watch_list is not None):
        # write into the stock
        for stock in watch_list:
            if stock not in stock_dict and len(stock_dict) < 10: #PARAM
                # HERE WOULD BE AI CLI SENTIMENT SCANNER
                process_list.append(subprocess.Popen(['python', 'main.py', stock], shell=True))
                stock_list.append(stock)
                stock_dict.add(stock)

        return True

    return False


def main():
    # Check if market is open or not...
    MARKET_OPEN_TIME = dt.time(9, 30, 0)  # 9:30 AM (24-hour format) PARAM
    MARKET_CLOSE_TIME = dt.time(16, 0, 0)  # 4:00 PM (24-hour format) PARAM
    PRE_MIDNIGHT = dt.time(23, 59, 59)
    POST_MIDNIGHT = dt.time(0, 0, 0)

    if  MARKET_CLOSE_TIME < dt.datetime.now().time() < PRE_MIDNIGHT \
            or POST_MIDNIGHT < dt.datetime.now().time() < MARKET_OPEN_TIME:
        print("The Market hasn't opened yet...")
        sleep_sec = get_seconds(9,30,0) # PARAM
        print(f"Sleeping for {sleep_sec} seconds until Marktet opens...")
        tm.sleep(sleep_sec)

    # variables that track the process
    stock_list = []
    stock_dict = set()
    process_list = []

    # get list of stocks available for trading
    check_list = False

    while (not check_list):
        print("Getting list of stocks to trade...")
        if dt.datetime.now().time() > MARKET_CLOSE_TIME:
            print("The Market has closed...")
            break
        else:
            # get list of stocks available for trading
            check_list = get_stock_start(stock_list,stock_dict,process_list)
            print(f"The Current active stocks are {stock_dict}")

            print("Sleeping for 15 minutes until next stock check...")
            tm.sleep(900) # PARAM

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

            # Get new stocks to add...
            print("Adding new stocks to the list...")
            get_stock_start(stock_list, stock_dict, process_list)
            print(f"The Current active stocks are {stock_dict}")

            print("Sleeping for 15 minutes until next stock check...")
            tm.sleep(900)  # PARAM

    return


if __name__ == "__main__":
    main()