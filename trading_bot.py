from stock_screener import get_undervalued_stocks


def main():
    # get list of stocks available for trading
    watch_list = get_undervalued_stocks()


if __name__=="__main__":
    main()