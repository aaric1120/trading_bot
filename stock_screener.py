from finvizfinance.screener.overview import Overview
import yfinance as yf

import subprocess
from random import shuffle
from param_reader import PARAM


def get_undervalued_stocks():
    """
    Returns a list of tickers with:

    - Positive Operating Margin
    - Debt-to-Equity ratio under 1
    - Low P/B (under 1)
    - Low P/E ratio (under 15)
    - Low PEG ratio (under 1)
    - Positive Insider Transactions
    """
    foverview = Overview()

    # filters_dict = {
    #                 'Price':'$1 to $20',
    #                 'Relative Volume':'Over 3',
    #                 'Average True Range':'Over 0.5',
    #                 'Beta':'Over 2'
    #                 }

    filters_dict = {'Price': 'Over $1',
                    'Average Volume':'Over 1M',
                    'Relative Volume': 'Over 3',
                    'Average True Range': 'Over 0.5'
                    }

    foverview.set_filter(filters_dict=filters_dict)
    df_overview = foverview.screener_view()

    if (df_overview is not None):
        tickers = df_overview['Ticker'].to_list()
        shuffle(tickers)
        return tickers

    return None


def get_stock_info(ticker):
    """
    basic info on theticke provided...
    :param ticker:
    :return:
    """
    stock = yf.Ticker(ticker)
    stock_info = {}

    # Get all available info (includes float, marketCap, averageVolume, etc.)
    info = stock.info

    # Extract data
    stock_info["floatShares"] = info.get("floatShares", "N/A")
    stock_info["marketCap"] = info.get("marketCap", "N/A")
    stock_info["averageVolume10days"] = info.get("averageVolume10days", "N/A")
    stock_info["averageVolume"] = info.get("averageVolume", "N/A")

    return stock_info


def get_stock_start(stock_list,stock_dict,process_list):
    """
    Starts the multi process for each stock trading...
    :param stock_list:
    :param stock_dict:
    :param process_list:
    :return:
    """
    # get set of stocks available for trading
    watch_list = get_undervalued_stocks()

    # print(f"Current list of available stockes to trade: {watch_list}")

    if (watch_list is not None):
        # write into the stock
        for stock in watch_list:
            if stock not in stock_dict and len(stock_dict) < int(PARAM["stock_number"]): #PARAM
                # HERE WOULD BE AI CLI SENTIMENT SCANNER
                process_list.append(subprocess.Popen(['python', 'main.py', stock], shell=True)) # PARAM
                stock_list.append(stock)
                stock_dict.add(stock)

        return True

    return False


# print(get_undervalued_stocks())
# # print(get_stock_info('BE'))
