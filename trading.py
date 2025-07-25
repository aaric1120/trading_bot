import math

from alpaca.broker import LimitOrderRequest
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestBarRequest


from alpaca.trading import TradingClient, TimeInForce
from pattern_detection import calculate_slope
from alpaca.trading.requests import GetOrdersRequest, ClosePositionRequest
from alpaca.trading.enums import OrderSide, QueryOrderStatus, OrderType

import logging
import time as tm
import datetime as dt

from TelegramBot import TelegramBot
from TimeConstants import LAST_MARKET_SELL, MARKET_CLOSE_TIME, MARKET_DEADLINE


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
    msg_bot = TelegramBot()

    def __init__(self,symbol, param, high, low, volume):
        self.param = param
        self.symbol = symbol
        self.highs = high
        self.lows = low
        self.hist_client = StockHistoricalDataClient(self.param["alpaca_key"], self.param["secret_key"])
        self.trade_client = TradingClient(self.param["alpaca_key"], self.param["secret_key"], paper=True)
        self.hist_request = StockLatestBarRequest(symbol_or_symbols=[self.symbol])
        self.volume = volume
        self.avg_vol = round(self.volume / len(self.highs), 2)

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

    def cancel_all(self):
        # Check if all the stock are sold
        self.trade_client = TradingClient(self.param["alpaca_key"],
                                          self.param["secret_key"], paper=True)

        # Get the current orders open for this symbol
        req = GetOrdersRequest(
            status=QueryOrderStatus.OPEN,
            symbols=[self.symbol]
        )
        orders = self.trade_client.get_orders(req)
        # Cancel all orders for the partial fil or non filled orders
        for order in orders:
            self.trade_client.cancel_order_by_id(str(order.id))

        return

    def get_available_shares(self):
        return int(self.trade_client.get_open_position(symbol_or_asset_id=self.symbol).qty_available)

    def monitor_order(self, stop_loss, take_profit, init_price):
        # wait 1 minute for order to fill
        tm.sleep(60)
        total_time = 0
        breakeven = False
        try:
            # cancel all trades
            self.cancel_all()

            # Get the number of stocks currently being traded
            curr_qty = self.get_available_shares()

            # If the current owned qty is 0. close the monitor
            if curr_qty == 0:
                return

            # else we start the 30 minute montioring
            while True:
                # Keep the loop alive without timeout
                self.hist_client = StockHistoricalDataClient(self.param["alpaca_key"],
                                                             self.param["secret_key"])
                self.trade_client = TradingClient(self.param["alpaca_key"],
                                                  self.param["secret_key"], paper=True)

                # Get latest close price
                latest_bar = self.hist_client.get_stock_latest_bar(self.hist_request)
                high, low, close = latest_bar[self.symbol].high, latest_bar[self.symbol].low, \
                                           latest_bar[self.symbol].close

                print(f"Current High asks for {self.symbol} is {self.highs[-1]}")
                print(f"Current Low asks for {self.symbol} is {self.lows[-1]}")
                print(f"Current Close is {close}")
                print(f"For {self.symbol}, the current stop loss is: {stop_loss}, and the current take profit is: {take_profit}")
                logging.info(latest_bar)
                logging.info(
                    f"For {self.symbol}, the current stop loss is: {stop_loss}, and the current take profit is: {take_profit}")

                # if Price is equal or above take profit
                if take_profit <= close:
                    # Cancel breakeven request
                    breakeven = False

                    # Cancel all trades not finished
                    self.cancel_all()

                    # Check how many shares are available
                    curr_qty = self.get_available_shares()

                    # is amount is zero, exit the trade...
                    if curr_qty == 0:
                        return

                    # check how many shares are left
                    if curr_qty == 1:
                        sell_qty = 1
                    else:
                        sell_qty = math.floor(curr_qty / 2) # PARAM

                    # Update take profit with latest close
                    take_profit = close

                    print(f"Placing order to sell {curr_qty} shares of {self.symbol} at price {take_profit}")
                    logging.info(f"Placing order to sell {curr_qty} shares of {self.symbol} at price {take_profit}")
                    # sell for take profit
                    limit_order_data = LimitOrderRequest(
                                                        symbol=self.symbol,
                                                        qty=int(sell_qty),
                                                        limit_price=round(take_profit,2),
                                                        side=OrderSide.SELL,
                                                        type=OrderType.LIMIT,
                                                        time_in_force=TimeInForce.DAY)

                    limit_order = self.trade_client.submit_order(order_data=limit_order_data)
                    print("TAKE PROFIT ORDER INFO:")
                    print(limit_order)
                    logging.info("TAKE PROFIT ORDER INFO:")
                    logging.info(limit_order)

                    # Send a notification
                    self.msg_bot.send_message(
                        "TAKE PROFIT", self.symbol, "SELL", take_profit, sell_qty, dt.datetime.now())

                    # if it was the last stock sold
                    if sell_qty == 1:
                        return

                    # Updated the take profit price
                    stop_loss = round(take_profit * self.param["tp_stop_loss"], 2)
                    take_profit = round(take_profit * self.param["take_profit"], 2)
                    init_price = round((take_profit + stop_loss) / 2, 2)
                    print(f"the updated take profit price is {take_profit}, the updated stop loss price is {stop_loss}")
                    logging.info(f"the updated take profit price is {take_profit}, the updated stop loss price is {stop_loss}")

                elif close <= stop_loss or total_time >= int(self.param["stock_retention"]*3) or \
                        dt.datetime.now().time() >= LAST_MARKET_SELL: # PARAM
                    print(f"Selling all of position with {self.symbol}...")
                    logging.info(f"Selling all of position with {self.symbol}...")

                    # cancel all position
                    self.cancel_all()

                    # Get the number of stocks currently available
                    curr_qty = self.get_available_shares()

                    # is amount is zero, exit the trade...
                    if curr_qty == 0:
                        return

                    print(f"The number of shares of {self.symbol} to liquidate is: {curr_qty}...")
                    logging.info(f"The number of shares of {self.symbol} to liquidate is: {curr_qty}...")

                    # Send a notification
                    self.msg_bot.send_message("STOP LOSS", self.symbol, "SELL", stop_loss, curr_qty,
                                              dt.datetime.now())

                    # Selling all positions...
                    self.trade_client.close_position(
                        symbol_or_asset_id=self.symbol,
                        close_options=ClosePositionRequest(
                            qty=str(curr_qty),
                        )
                    )
                    return

                # Once half of retention period was been met without shares being sold
                elif not breakeven and int(self.param["stock_retention"]*3*self.param["breakeven"]) \
                        < total_time < int(self.param["stock_retention"]*3):
                    # Set breakeven filter to true
                    breakeven = True

                    # Cancel all trades not finished
                    self.cancel_all()

                    # Check how many shares are available
                    curr_qty = self.get_available_shares()

                    # is amount is zero, exit the trade...
                    if curr_qty == 0:
                        return

                    print(f"Placing order to sell {curr_qty} shares of {self.symbol} at price {init_price}")
                    logging.info(f"Placing order to sell {curr_qty} shares of {self.symbol} at price {init_price}")
                    # sell for take profit
                    limit_order_data = LimitOrderRequest(
                                                        symbol=self.symbol,
                                                        qty=curr_qty,
                                                        limit_price=round(init_price,2),
                                                        side=OrderSide.SELL,
                                                        type=OrderType.LIMIT,
                                                        time_in_force=TimeInForce.DAY)

                    limit_order = self.trade_client.submit_order(order_data=limit_order_data)
                    print("BREAK EVEN ORDER INFO:")
                    print(limit_order)
                    logging.info("BREAK EVEN ORDER INFO:")
                    logging.info(limit_order)

                    # Send a notification
                    self.msg_bot.send_message("BREAK EVEN", self.symbol, "SELL", init_price, curr_qty,
                                              dt.datetime.now())

                # Wait 1/3 minute for latest bar (PARAM)
                total_time += 1
                tm.sleep(20)

        except Exception as e:
            print(f"Error doing order monitoring: {e}")
            logging.info(e)

        return

    def run(self):
        breakout = False
        breakdown = False

        try:
            while(True):
                # Keep the loop alive
                self.hist_client = StockHistoricalDataClient(self.param["alpaca_key"],
                                                             self.param["secret_key"])
                latest_bar = self.hist_client.get_stock_latest_bar(self.hist_request)
                high, low, close, volume = latest_bar[self.symbol].high, latest_bar[self.symbol].low,\
                                           latest_bar[self.symbol].close, latest_bar[self.symbol].volume

                # Check if data is repeated
                if high != self.highs[-1] and low != self.lows[-1]:
                    self.highs.append(high)
                    self.lows.append(low)
                    self.volume += volume
                    self.get_new_avg()

                    print(f"Current High asks for {self.symbol} is {self.highs[-1]}")
                    print(f"Current Low asks for {self.symbol} is {self.lows[-1]}")
                    print(f"Current Close is {close}")
                    print(f"Current resistance is: {self.resist} and support is: {self.support}")
                    print(f"Current average volume is: {self.avg_vol}")

                    logging.info(latest_bar)
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

                    elif close > self.resist and breakout and (self.avg_vol*self.param["volume_mult"] > volume
                                                               or self.avg_vol < self.param["volume_threshold"]):
                        print(f"The current close: {close} is above the resistance of {self.resist}, but volume isn't enough...")
                        logging.info(
                            f"The current close: {close} is above the resistance of {self.resist}, but volume isn't enough...")
                        self.get_new_lines()
                        print(f"Updated resistance to: {self.resist} and support to: {self.support}")
                        logging.info(f"Updated resistance to: {self.resist} and support to: {self.support}")

                    # second bar also closes above resistance: BUY
                    elif close > self.resist and breakout and (self.avg_vol*self.param["volume_mult"] <= volume) and \
                            (self.avg_vol >= self.param["volume_threshold"]):
                        if dt.datetime.now().time() >= MARKET_DEADLINE:
                            print("The current time is past the last buy deadline...")
                            logging.info("The current time is past the last buy deadline...")
                            logging.info("====ClOSING TRADE====")
                            return

                        print(f"The current close: {close} is above the resistance of {self.resist}. Placing Order...")
                        logging.info(f"The current close: {close} is above the resistance of {self.resist}. Placing Order...")
                        print(f"The current volume: {volume} is higher than the average volume: {self.avg_vol} by required factor")
                        logging.info(
                            f"The current volume: {volume} is higher than the average volume: {self.avg_vol} by required factor")

                        # Set stop loss at just below resistance
                        stop_loss = round(self.resist * self.param["stop_loss"], 2)

                        price = round(close * self.param["price"], 2)

                        take_profit = round(price * self.param["take_profit"], 2)

                        quantity = math.floor(float(self.trade_client.get_account().cash) / price)

                        if quantity < 1:
                            print("insufficient funds to make purchase...ending trade ")
                            logging.info("insufficient funds to make purchase...ending trade ")
                            logging.info("====ClOSING TRADE====")
                            return

                        # do the buy
                        limit_order_data = LimitOrderRequest(
                                                        symbol=self.symbol,
                                                        qty=quantity,
                                                        limit_price=price,
                                                        side=OrderSide.BUY,
                                                        type=OrderType.LIMIT,
                                                        time_in_force=TimeInForce.DAY)

                        print(limit_order_data)

                        # place the order
                        self.trade_client = TradingClient(self.param["alpaca_key"],
                                                          self.param["secret_key"], paper=True)

                        limit_order = self.trade_client.submit_order(order_data=limit_order_data)
                        print(limit_order)
                        logging.info("ORDER INFO:")
                        logging.info(limit_order)

                        # Send a notification
                        self.msg_bot.send_message("BUY IN", self.symbol, "BUY", price, quantity,
                                                  dt.datetime.now())

                        # Start the monitoring of the order
                        print(f"Starting the monitoring of {self.symbol}, the current take profit is: {take_profit}, the current stop loss is: {stop_loss}")
                        logging.info(
                            f"Starting the monitoring of {self.symbol}, the current take profit is: {take_profit}, the current stop loss is: {stop_loss}")
                        self.monitor_order(stop_loss,take_profit,close)

                        logging.info("====ClOSING TRADE====")
                        return

                    elif close < self.support and not breakdown:
                        print(f"close price: {close} just dropped below support of {self.support}...")
                        logging.info(f"close price: {close} just dropped below support of {self.support}...")
                        breakdown, breakout = True, False

                    elif close < self.support and breakdown:
                        print(f"Closing price: {close} just dropped below support {self.support} again...ending trade...")
                        logging.info(
                            f"Closing price: {close} just dropped below support {self.support} again...ending trade...")

                        return

                # Bar updates every Minute for latest data unless initial breakout, then half the time (PARAM)
                if not breakout:
                    tm.sleep(60)
                else:
                    tm.sleep(30)

                # Check close time for market
                if dt.datetime.now().time() >= MARKET_CLOSE_TIME:
                    logging.info("The Market is closed...")
                    print("The Market is closed...")
                    return

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
        self.resist = round(self.high_slope * len(self.highs) + (max(self.highs) - self.high_slope * self.highs.index(max(self.highs))),3)
        self.support = round(self.low_slope * len(self.lows) + (min(self.lows) - self.low_slope * self.lows.index(min(self.lows))),3)

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
        self.support = round(self.low_slope * len(self.lows) + (min(self.lows) - self.low_slope * self.lows.index(min(self.lows))),3)
        return


class DescendingTriangle(TriangleTrade):
    def get_new_lines(self):
        self.support = min(self.lows)

        self.high_slope, self.high_const, _ = calculate_slope(self.highs)
        self.resist = round(self.high_slope * len(self.highs) + (max(self.highs) - self.high_slope * self.highs.index(max(self.highs))), 3)
        return

