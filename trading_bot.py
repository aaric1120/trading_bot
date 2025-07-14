import time
import datetime as dt

from stock_screener import get_undervalued_stocks
import subprocess


def get_stock_start(stock_list,stock_dict,process_list):
    # get list of stocks available for trading
    watch_list = get_undervalued_stocks()

    print(f"Current list of available stockes to trade: {watch_list}")

    # write into the stocks
    for stock in watch_list:
        if stock not in stock_dict:
            process_list.append(subprocess.Popen(['python', 'main.py', stock], shell=True))
            stock_list.append(stock)
            stock_dict.add(stock)

    return


def main():
    # variables that track the proces
    stock_list = []
    stock_dict = set()
    process_list = []

    # get list of stocks available for trading
    get_stock_start(stock_list,stock_dict,process_list)

    while len(stock_dict) != 0:
        # Check if the process has finished
        for i in range(len(stock_list)):
            if(stock_list[i] is not None):
                if process_list[i].poll() is not None:
                    stock_dict.remove(stock_list[i])
                    stock_list[i] = None

        time.sleep(900)
        # get list of stocks available for trading
        # Check close time for market
        MARKET_CLOSE_TIME = dt.time(16, 0, 0)  # 4:00 PM (24-hour format)
        if dt.datetime.now().time() > MARKET_CLOSE_TIME:
            print("The Market has closed...")
            break
        else:
            get_stock_start(stock_list, stock_dict, process_list)


if __name__ == "__main__":
    main()