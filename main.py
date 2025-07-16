from param_reader import param_reader

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestBarRequest

import datetime as dt
import time as tm

import numpy as np

from pattern_detection import pattern_detection

from trading import RectangleTrade, AscendingTriangle, DescendingTriangle, TriangleTrade

import sys
import logging


def main():
    # Get the stock to trade
    curr_symbol = sys.argv[-1]
    print(f"Currently Trading the stock: {curr_symbol}")

    # Configure logging
    logging.FileHandler(f"logs/trade_log_{curr_symbol}_{dt.datetime.today().strftime('%Y-%m-%d')}.txt", mode="a",
                        encoding=None, delay=False)
    logging.basicConfig(
        filename=f"logs/trade_log_{curr_symbol}_{dt.datetime.today().strftime('%Y-%m-%d')}.txt",  # file to write
        level=logging.INFO,  # log INFO and above
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.info("=== Strategy started ===")
    # read the parameters from file
    param = param_reader("param.txt")

    logging.info(f"Start collecting the current highs/lows for: {curr_symbol}")

    # Gather 20 minutes of stock price after market opens
    hist_stock_client = StockHistoricalDataClient('PKIY6QW5KN7LAQ8BKRRZ', 'za8w8gjyhg7nFLy3eQgEMbZgtODc3QUnswp2jc5V')
    get_stock_price = StockLatestBarRequest(symbol_or_symbols=[curr_symbol])

    highs=[]
    lows=[]
    volume=0.0

    # Get the initial data
    get_stock_price_data = hist_stock_client.get_stock_latest_bar(get_stock_price)
    logging.info(f"Most recent stock data: {get_stock_price_data}")
    highs.append(get_stock_price_data[curr_symbol].high)
    lows.append(get_stock_price_data[curr_symbol].low)

    while(True):
        # Keep connection in loop to stop timeouts
        hist_stock_client = StockHistoricalDataClient('PKIY6QW5KN7LAQ8BKRRZ',
                                                      'za8w8gjyhg7nFLy3eQgEMbZgtODc3QUnswp2jc5V')
        get_stock_price_data = hist_stock_client.get_stock_latest_bar(get_stock_price)

        if (highs[-1] != get_stock_price_data[curr_symbol].high and lows[-1] != get_stock_price_data[curr_symbol].low):
            logging.info(f"Most recent stock data: {get_stock_price_data}")
            highs.append(get_stock_price_data[curr_symbol].high)
            lows.append(get_stock_price_data[curr_symbol].low)
            volume += get_stock_price_data[curr_symbol].volume
            print("Current Stock is: " + curr_symbol)
            print(highs)
            print(lows)

            if (len(highs) > param["sample_minutes"]):
                logging.info(f"Collected {param['sample_minutes']} minutes of data, trying to match pattern...")
                pattern, high_slp, high_C, low_slp, low_C, rect_min, rect_max = pattern_detection(np.array(highs), np.array(lows))
                print("The detected pattern is: " + pattern)
                if (pattern == "no_pattern"):
                    logging.info("no pattern detected...collecting more data points...")
                    # if for 30 min, truncate to latest 5 minutes and try again
                    if (len(highs) > int(param["minute_limit"])):
                        logging.info(f"Data points limit reached {param['minute_limit']}, reducing to most recent {param['retention']} points.")
                        highs = highs[int(param["minute_limit"] - param["retention"]):]
                        lows = lows[int(param["minute_limit"] - param["retention"]):]

                elif (pattern == "rectangle"):
                    logging.info("Pattern matched as Rectangle, starting trading strategy")
                    Rect_trading = RectangleTrade(curr_symbol,param, highs, lows, volume,rect_max, rect_min)
                    Rect_trading.run()
                    break

                elif (pattern == "symmetrical_triangle"):
                    logging.info("Pattern matched as Symmetrical Triangle, starting trading strategy")
                    Tri_trading = TriangleTrade(curr_symbol, param, highs,lows, volume,high_slp,high_C,low_slp,low_C)
                    Tri_trading.run()
                    break

                elif (pattern == "ascending_triangle"):
                    logging.info("Pattern matched as Ascending Triangle, starting trading strategy")
                    ATri_trade = AscendingTriangle(curr_symbol, param, highs,lows, volume, high_slp,high_C,low_slp,low_C)
                    ATri_trade.run()
                    break

                elif (pattern == "descending_trianlge"):
                    logging.info("Pattern matched as Descending Trianlge, starting trading strategy")
                    DTri_trade = DescendingTriangle(curr_symbol, param, highs,lows, volume, high_slp,high_C,low_slp,low_C)
                    DTri_trade.run()
                    break

        # Wait 60 seconds for next bar
        tm.sleep(60)

        # Check close time for market
        MARKET_CLOSE_TIME = dt.time(16, 0,0)  # 4:00 PM (24-hour format)
        if dt.datetime.now().time() > MARKET_CLOSE_TIME:
            print("The Market has closed...")
            break

        print(f"The Timestamp is {dt.datetime.now()}")


if __name__=="__main__":
    main()

