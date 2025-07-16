import math

from alpaca.broker import LimitOrderRequest
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestBarRequest


from alpaca.trading import TradingClient, OrderSide, TimeInForce, OrderClass, TakeProfitRequest, StopLossRequest
from pattern_detection import calculate_slope

import logging
import datetime as dt
import time as tm


class BaseTrade:
    highs = []
    lows = []
    hist_client = None
    hist_request = None
    symbol = ""
    resist = 0
    support = 0
    param = None
    volume = 0.0
    avg_vol = 0.0

    def __init__(self,symbol, param, high, low, volume):
        self.symbol = symbol
        self.highs = high
        self.lows = low
        self.hist_client = StockHistoricalDataClient('PKIY6QW5KN7LAQ8BKRRZ', 'za8w8gjyhg7nFLy3eQgEMbZgtODc3QUnswp2jc5V')
        self.trade_client = TradingClient('PKIY6QW5KN7LAQ8BKRRZ', 'za8w8gjyhg7nFLy3eQgEMbZgtODc3QUnswp2jc5V', paper=True)
        self.hist_request = StockLatestBarRequest(symbol_or_symbols=[self.symbol])
        self.param = param
        self.volume = volume
        self.avg_vol = round(self.volume / len(self.highs) , 2)

        # Configure logging
        logging.FileHandler(f"logs/trade_log_{self.symbol}_{dt.datetime.today().strftime('%Y-%m-%d')}.txt", mode="a",
                            encoding=None, delay=False)
        logging.basicConfig(
            filename=f"logs/trade_log_{self.symbol}_{dt.datetime.today().strftime('%Y-%m-%d')}.txt",  # file to write
            level=logging.INFO,  # log INFO and above
            format="%(asctime)s %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    def get_new_lines(self):
        return

    def get_new_avg(self):
        self.avg_vol = round(self.volume / len(self.highs), 2)

    def run(self):
        breakout = False
        breakdown = False

        try:
            while(True):
                self.hist_client = StockHistoricalDataClient('PKIY6QW5KN7LAQ8BKRRZ',
                                                             'za8w8gjyhg7nFLy3eQgEMbZgtODc3QUnswp2jc5V')
                latest_bar = self.hist_client.get_stock_latest_bar(self.hist_request)
                high, low, close, volume = latest_bar[self.symbol].high, latest_bar[self.symbol].low,\
                                           latest_bar[self.symbol].close, latest_bar[self.symbol].volume

                # Check if data is repeated
                if high != self.highs[-1] and low != self.lows[-1]:
                    self.highs.append(high)
                    self.lows.append(low)
                    self.volume += volume
                    self.get_new_avg()
                    # self.get_new_lines()

                    print(f"Current High asks for {self.symbol} is {self.highs[-1]}")
                    print(f"Current Low asks for {self.symbol} is {self.lows[-1]}")
                    print(f"Current Close is {close}")
                    print(f"Current resistance is: {self.resist} and support is: {self.support}")
                    print(f"Current average volume is: {self.avg_vol}")

                    logging.info(f"Current High asks for {self.symbol} is {self.highs[-1]}")
                    logging.info(f"Current Low asks for {self.symbol} is {self.lows[-1]}")
                    logging.info(f"Current Close is {close}")
                    logging.info(f"Current resistance is: {self.resist} and support is: {self.support}")
                    logging.info(f"Current average volume is: {self.avg_vol}")

                    # If close between resistance and support, update the line
                    if self.support < close < self.resist:
                        self.get_new_lines()
                        print(f"Updated resistance to: {self.resist} and support to: {self.support}")
                        logging.info(f"Updated resistance to: {self.resist} and support to: {self.support}")
                        breakout, breakdown = False, False

                    # if resistance is broken initially
                    elif close > self.resist and not breakout:
                        # set breakout check to true
                        print(f"The Current Close {close} is above the resistance...")
                        logging.info(f"The Current Close {close} is above the resistance...")
                        self.get_new_lines()
                        print(f"Updated resistance to: {self.resist} and support to: {self.support}")
                        logging.info(f"Updated resistance to: {self.resist} and support to: {self.support}")
                        breakout, breakdown = True, False

                    elif close > self.resist and breakout and (self.avg_vol*self.param["volume_mult"] > volume):
                        print(f"The current close: {close} is above the resistance of {self.resist}, but volume isn't enough...")
                        logging.info(
                            f"The current close: {close} is above the resistance of {self.resist}, but volume isn't enough...")
                        self.get_new_lines()
                        print(f"Updated resistance to: {self.resist} and support to: {self.support}")
                        logging.info(f"Updated resistance to: {self.resist} and support to: {self.support}")

                    # second bar also closes above resistance: BUY
                    elif close > self.resist and breakout and (self.avg_vol*self.param["volume_mult"] <= volume):
                        print(f"The current close: {close} is above the resistance of {self.resist}. Placing Order...")
                        logging.info(f"The current close: {close} is above the resistance of {self.resist}. Placing Order...")
                        print(f"The current volume: {volume} is higher than the average volume: {self.avg_vol} by required factor")
                        logging.info(
                            f"The current volume: {volume} is higher than the average volume: {self.avg_vol} by required factor")

                        # Set stop loss at just below resistance
                        stop_loss = round(self.resist * self.param["stop_loss"], 2) #PARAM

                        price = round(close * self.param["price"],2)  # PARAM

                        take_profit = round(price * self.param["take_profit"],2)  # PARAM

                        quantity = math.floor(float(self.trade_client.get_account().cash) / price)

                        # do the buy
                        limit_order_data = LimitOrderRequest(
                                                symbol=self.symbol,
                                                limit_price=price,
                                                qty=quantity,
                                                side=OrderSide.BUY,
                                                time_in_force=TimeInForce.DAY,
                                                order_class=OrderClass.BRACKET,
                                                take_profit=TakeProfitRequest(limit_price=take_profit),
                                                stop_loss=StopLossRequest(stop_price=stop_loss))

                        print(limit_order_data)

                        # place the order
                        self.trade_client = TradingClient('PKIY6QW5KN7LAQ8BKRRZ',
                                                          'za8w8gjyhg7nFLy3eQgEMbZgtODc3QUnswp2jc5V', paper=True)
                        limit_order = self.trade_client.submit_order(order_data=limit_order_data)
                        print(limit_order)
                        logging.info("ORDER INFO:")
                        logging.info(limit_order)
                        logging.info("====ClOSING TRADE====")
                        break

                    elif close < self.support and not breakdown:
                        print(f"close price: {close} just dropped below support of {self.support}...")
                        logging.info(f"close price: {close} just dropped below support of {self.support}...")
                        breakdown, breakout = True, False

                    elif close < self.support and breakdown:
                        print(f"Closing price: {close} just dropped below support {self.support} again...ending trade...")
                        logging.info(
                            f"Closing price: {close} just dropped below support {self.support} again...ending trade...")

                        break

                # Bar updates every Minute for latest data
                tm.sleep(60)

                # Check close time for market
                MARKET_CLOSE_TIME = dt.time(16, 0,0)  # 4:00 PM (24-hour format)
                if dt.datetime.now().time() > MARKET_CLOSE_TIME:
                    logging.info("The Market is closed...")
                    print("The Market is closed...")
                    break;

                print(f"The Timestamp is {dt.datetime.now()}")

        except Exception as e:
            print(e)
            logging.error(e)


class TriangleTrade(BaseTrade):
    high_slope = 0
    low_slope = 0
    high_const = 0
    low_const = 0

    def __init__(self, symbol,param, high, low, volume, h_slope, h_const, l_slope, l_const):
        super().__init__(symbol,param, high, low, volume)
        self.high_slope=h_slope
        self.high_const=h_const
        self.low_slope=l_slope
        self.low_const=l_const

        # run the get new line once to get resistance/support
        self.get_new_lines()

    def get_new_lines(self):
        # calculate the slops for both
        self.high_slope, self.high_const,_ = calculate_slope(self.highs)
        self.low_slope, self.low_const,_ = calculate_slope(self.lows)

        # calculate the current resistance/support line to pass through the max/min of the highs/lows
        self.resist = self.high_slope * len(self.highs) + (max(self.highs) - self.high_slope * self.highs.index(max(self.highs)))
        self.support = self.low_slope * len(self.lows) + (min(self.lows) - self.low_slope * self.lows.index(min(self.lows)))

        return


class RectangleTrade(BaseTrade):

    def __init__(self, symbol,param, high, low, volume, resist, support):
        super().__init__(symbol,param, high, low, volume)
        self.resist = resist
        self.support = support

    def get_new_lines(self):
        self.resist = max(self.resist, self.highs[-1])
        self.support = min(self.support, self.lows[-1])
        return


class AscendingTriangle(TriangleTrade):
    def get_new_lines(self):
        self.resist = max(self.highs)

        self.low_slope, self.low_const, _ = calculate_slope(self.lows)
        self.support = self.low_slope * len(self.lows) + (min(self.lows) - self.low_slope * self.lows.index(min(self.lows)))
        return


class DescendingTriangle(TriangleTrade):
    def get_new_lines(self):
        self.support = min(self.lows)

        self.high_slope, self.high_const, _ = calculate_slope(self.highs)
        self.resist = self.high_slope * len(self.highs) + (max(self.highs) - self.high_slope * self.highs.index(max(self.highs)))
        return

