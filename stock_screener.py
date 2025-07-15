from finvizfinance.screener.overview import Overview
import yfinance as yf


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

    filters_dict = {'Float':'Under 20M',
                    'Price':'$1 to $20',
                    'Relative Volume':'Over 3',
                    'Current Volume':'Over 500K',
                    'Average True Range':'Over 0.5',
                    'Beta':'Over 2'
                    }

    foverview.set_filter(filters_dict=filters_dict)
    df_overview = foverview.screener_view()
    # if not os.path.exists('out'):  # ensures you have an 'out' folder ready
    #     os.makedirs('out')
    # df_overview.to_csv('out/Overview.csv', index=False)
    tickers = df_overview['Ticker'].to_list()
    # print("Current list of valid stocks...")
    # print(tickers)
    return tickers


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

    print(f"Float: {stock_info['floatShares']} shares")
    print(f"Market Cap: ${stock_info['marketCap'] / 1e9:.2f}B")  # Convert to billions
    print(f"10-Day Avg Volume: {stock_info['averageVolume10days']:,} shares")
    print(f"3-Month Avg Volume: {stock_info['averageVolume']:,} shares")

    return stock_info

# print(get_undervalued_stocks())
