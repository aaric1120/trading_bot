from param_reader import param_reader

from stock_screener import get_undervalued_stocks

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestBarRequest

from datetime import datetime,date
from alpaca.data import TimeFrame

import numpy as np

from pattern_detection import pattern_detection

from trading import *


def main():
    # read the parameters from file
    param = param_reader("param.txt")

    # Create the list of stocks to watch, for now just find one (test)
    watch_list = get_undervalued_stocks()
    watch_list = ['AAPL', 'NVDA']
    curr_symbol = watch_list[0]

    # Gather 20 minutes of stock price after market opens
    hist_stock_client = StockHistoricalDataClient('PKIY6QW5KN7LAQ8BKRRZ', 'za8w8gjyhg7nFLy3eQgEMbZgtODc3QUnswp2jc5V')
    get_stock_price = StockLatestBarRequest(symbol_or_symbols=[curr_symbol])

    highs=[]
    lows=[]

    # Get the initial data
    get_stock_price_data = hist_stock_client.get_stock_latest_bar(get_stock_price)
    highs.append(get_stock_price_data[curr_symbol].high)
    lows.append(get_stock_price_data[curr_symbol].low)

    while(True):
        # Keep connection in loop to stop timeouts
        hist_stock_client = StockHistoricalDataClient('PKIY6QW5KN7LAQ8BKRRZ',
                                                      'za8w8gjyhg7nFLy3eQgEMbZgtODc3QUnswp2jc5V')
        get_stock_price_data = hist_stock_client.get_stock_latest_bar(get_stock_price)

        if (highs[-1] != get_stock_price_data[curr_symbol].high and lows[-1] != get_stock_price_data[curr_symbol].low):
            highs.append(get_stock_price_data[curr_symbol].high)
            lows.append(get_stock_price_data[curr_symbol].low)
            print("Current Stock is: " + curr_symbol)
            print(highs)
            print(lows)

        if (len(highs) > param["sample_minutes"]):
            pattern, high_slp, high_C, low_slp, low_C, rect_min, rect_max = pattern_detection(np.array(highs), np.array(lows))
            print("The detected pattern is: " + pattern)
            if (pattern == "no_pattern"):
                # if for 30 min, truncate to latest 5 minutes and try again
                if (len(highs) > int(param["minute_limit"])):
                    highs = highs[int(param["minute_limit"] - param["retention"]):]
                    lows = lows[int(param["minute_limit"] - param["retention"]):]

            elif (pattern == "rectangle"):
                Rect_trading = RectangleTrade(curr_symbol,param, highs, lows,rect_max, rect_min)
                Rect_trading.run()
                break

            elif (pattern == "symmetrical_triangle"):
                Tri_trading = TriangleTrade(curr_symbol, param, highs,lows,high_slp,high_C,low_slp,low_C)
                Tri_trading.run()
                break

            elif (pattern == "ascending_triangle"):
                ATri_trade = AscendingTriangle(curr_symbol, param, highs,lows,high_slp,high_C,low_slp,low_C)
                ATri_trade.run()
                break

            elif (pattern == "descending_trianlge"):
                DTri_trade = DescendingTriangle(curr_symbol, param, highs,lows,high_slp,high_C,low_slp,low_C)
                DTri_trade.run()
                break

        # Wait 60 seconds for next bar
        time.sleep(60)


if __name__=="__main__":
    main()

