import math
import time
import matplotlib.pyplot as plt

from alpaca.broker import LimitOrderRequest
from alpaca.data.historical import StockHistoricalDataClient, NewsClient
from alpaca.data.requests import StockLatestQuoteRequest, StockLatestTradeRequest, StockLatestBarRequest,\
    StockSnapshotRequest, NewsRequest, StockBarsRequest

from alpaca.trading import TradingClient, OrderSide, TimeInForce, OrderClass, TakeProfitRequest, StopLossRequest
from pattern_detection import calculate_slope

from param_reader import param_reader

class BaseTrade:
    highs = []
    lows = []
    hist_client = None
    hist_request = None
    symbol = ""
    resist = 0
    support = 0
    param = None

    def __init__(self,symbol, param, high, low):
        self.symbol = symbol
        self.highs = high
        self.lows = low
        self.hist_client = StockHistoricalDataClient('PKIY6QW5KN7LAQ8BKRRZ', 'za8w8gjyhg7nFLy3eQgEMbZgtODc3QUnswp2jc5V')
        self.trade_client = TradingClient('PKIY6QW5KN7LAQ8BKRRZ', 'za8w8gjyhg7nFLy3eQgEMbZgtODc3QUnswp2jc5V', paper=True)
        self.hist_request = StockLatestBarRequest(symbol_or_symbols=[self.symbol])
        self.param = param

    def get_new_lines(self):
        return

    def run(self):
        breakout = False
        breakdown = False

        try:
            while(True):
                self.hist_client = StockHistoricalDataClient('PKIY6QW5KN7LAQ8BKRRZ',
                                                             'za8w8gjyhg7nFLy3eQgEMbZgtODc3QUnswp2jc5V')
                latest_bar = self.hist_client.get_stock_latest_bar(self.hist_request)
                high, low, close = latest_bar[self.symbol].high, latest_bar[self.symbol].low, latest_bar[self.symbol].close

                # Check if data is repeated
                if high != self.highs[-1] and low != self.lows[-1]:
                    self.highs.append(high)
                    self.lows.append(low)
                    print(f"Current High asks for {self.symbol} is {self.highs[-1]}")
                    print(f"Current Low asks for {self.symbol} is {self.lows[-1]}")
                    print(f"Current Close is {close}")
                    print(f"Current resistance is: {self.resist} and support is: {self.support}")

                    # If close between resistance and support, update the line
                    if self.support < close < self.resist:
                        self.get_new_lines()
                        print(f"Updated resistance to: {self.resist} and support to: {self.support}")
                        breakout, breakdown = False, False

                    # if resistance is broken initially
                    elif close > self.resist and not breakout:
                        # set breakout check to true
                        print(f"The Current Close {close} is above the resistance...")
                        breakout, breakdown = True, False

                    # second bar also closes above resistance: BUY
                    elif close > self.resist and breakout:
                        print(f"The current close: {close} is above the resistance of {self.resist}. Placing Order...")
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
                                                time_in_force=TimeInForce.GTC,
                                                order_class=OrderClass.BRACKET,
                                                take_profit=TakeProfitRequest(limit_price=take_profit),
                                                stop_loss=StopLossRequest(stop_price=stop_loss))

                        print(limit_order_data)

                        # place the order
                        limit_order = self.trade_client.submit_order(order_data=limit_order_data)
                        print(limit_order)
                        break

                    elif close < self.support and not breakdown:
                        print(f"close price: {close} just dropped below support of {self.support}...")
                        breakdown, breakout = True, False

                    elif close < self.support and breakdown:
                        print(f"Closing price: {close} just dropped below support {self.support} again...ending trade...")
                        break

                # Bar updates every Minute for latest data
                time.sleep(60)
        except Exception as e:
            print(e)


class TriangleTrade(BaseTrade):
    high_slope = 0
    low_slope = 0
    high_const = 0
    low_const = 0

    def __init__(self, symbol,param, high, low, h_slope, h_const, l_slope, l_const):
        super().__init__(symbol,param, high, low)
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

    def __init__(self, symbol,param, high, low, resist, support):
        super().__init__(symbol,param, high, low)
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

