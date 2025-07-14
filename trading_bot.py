import time

from stock_screener import get_undervalued_stocks
import subprocess


def main():
    # get list of stocks available for trading
    watch_list = get_undervalued_stocks()
    watch_list = ['NVDA','TSLA']

    # variables that track the proces
    stock_list = []
    stock_dict = set()
    process_list = []

    # write into the stocks
    for stock in watch_list:
        process_list.append(subprocess.Popen(['python','main.py',stock],shell=True))
        stock_list.append(stock)
        stock_dict.add(stock)

    while len(stock_dict) != 0:
        # Check if the process has finished
        for i in range(len(stock_list)):
            if(stock_list[i] is not None):
                if process_list[i].poll() is not None:
                    stock_dict.remove(stock_list[i])
                    stock_list[i] = None

        time.sleep(300)
        for proc in process_list:
            proc.kill();


if __name__=="__main__":
    main()