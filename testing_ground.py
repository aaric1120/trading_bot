from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time


class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.nextValidOrderId = None

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        print("Next Valid Order ID:", orderId)

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId,
                    whyHeld, mktCapPrice):
        print(
            f"OrderStatus. Id: {orderId}, Status: {status}, Filled: {filled}, Remaining: {remaining}, AvgFillPrice: {avgFillPrice}")

    def openOrder(self, orderId, contract, order, orderState):
        print(
            f"OpenOrder. ID: {orderId}, {contract.symbol}, {contract.secType}, {contract.currency}, {order.action}, {order.orderType}, {order.totalQuantity}, {orderState.status}")

    def execDetails(self, reqId, contract, execution):
        print(
            f"ExecDetails. {contract.symbol}, {contract.secType}, {execution.side}, {execution.shares}, {execution.price}")


def run_loop(app):
    app.run()


app = IBapi()
app.connect('127.0.0.1', 7497, 123)  # 7497 for paper trading

# Start the socket in a thread
api_thread = threading.Thread(target=run_loop, args=(app,), daemon=True)
api_thread.start()

time.sleep(1)  # Sleep interval to allow time for connection to setup

if not app.isConnected():
    print("Failed to connect")
    exit()

def create_contract(symbol, sec_type='STK', exchange='SMART', currency='USD'):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.exchange = exchange
    contract.currency = currency
    return contract

# Example for Apple stock
apple_contract = create_contract('AAPL')


def create_order(action, quantity, order_type, price=None, tif='DAY'):
    order = Order()
    order.action = action  # 'BUY' or 'SELL'
    order.totalQuantity = quantity
    order.orderType = order_type  # 'MKT', 'LMT', 'STP', etc.
    order.tif = tif  # 'DAY', 'GTC' (Good Till Canceled)

    if price is not None:
        order.lmtPrice = price  # Required for limit orders

    return order


# Market order example
market_order = create_order('BUY', 10, 'MKT')

# Limit order example
limit_order = create_order('SELL', 5, 'LMT', 150.50)

# Wait until we have the next valid order ID
while app.nextValidOrderId is None:
    app.nextValidId(1000)
    time.sleep(0.1)

# Place market order
app.placeOrder(app.nextValidOrderId, apple_contract, market_order)
print(f"Placed market order with ID: {app.nextValidOrderId}")
app.nextValidOrderId += 1

# Place limit order
app.placeOrder(app.nextValidOrderId, apple_contract, limit_order)
print(f"Placed limit order with ID: {app.nextValidOrderId}")

# Let the order events come through
time.sleep(3)
app.disconnect()
# import math
#
# from matplotlib import pyplot as plt
# from pydantic_core import TzInfo
#
# from alpaca.trading.client import TradingClient
# from time_tools import get_current_date

# from alpaca.trading.requests import GetOrdersRequest, ClosePositionRequest
# from alpaca.trading.enums import OrderSide, QueryOrderStatus, OrderType
# from alpaca.trading.requests import GetAssetsRequest
# from alpaca.trading.enums import AssetClass

# from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, TakeProfitRequest, StopLossRequest
# from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass
# from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
# from datetime import datetime, tzinfo, date, timezone
# import pytz
# from alpaca.data.live import StockDataStream
# import pandas as pd
#
# from alpaca.data.historical import StockHistoricalDataClient, NewsClient
# from alpaca.data.requests import StockLatestQuoteRequest, StockLatestTradeRequest, StockLatestBarRequest,\
#     StockSnapshotRequest, NewsRequest, StockBarsRequest
#
# import time_tools
# import numpy as np
# import yfinance as yf
#
from param_reader import param_reader

from pattern_detection import *
param = param_reader("param.txt")
#
#
# # Request Examples
# trading_client = TradingClient(param["alpaca_key"], param["secret_key"], paper=True)

# print(get_current_date()[0])
#
# hist_data_client = StockHistoricalDataClient('PKIY6QW5KN7LAQ8BKRRZ', 'za8w8gjyhg7nFLy3eQgEMbZgtODc3QUnswp2jc5V')
#
# news_data_client = NewsClient('PKIY6QW5KN7LAQ8BKRRZ', 'za8w8gjyhg7nFLy3eQgEMbZgtODc3QUnswp2jc5V')
#
# wss_client = StockDataStream('PKIY6QW5KN7LAQ8BKRRZ', 'za8w8gjyhg7nFLy3eQgEMbZgtODc3QUnswp2jc5V')
#
#
# print(trading_client.get_account())
# print(trading_client.get_open_position(symbol_or_asset_id='NVDA').qty_available)

# # params to filter orders by
# request_params = GetOrdersRequest(
#                     symbol='NVDA',
#                     status=QueryOrderStatus.OPEN,
#                     side=OrderSide.BUY
#                  )

# orders that satisfy params
# orders = trading_client.get_orders(filter=request_params)
#
# print(orders)

# get a list of orders including closed (e.g. filled) orders by specifying symbol
# req = GetOrdersRequest(
#     status = QueryOrderStatus.OPEN,
#     symbols = ['NVDA']
# )
# orders = trading_client.get_orders(req)
# print(orders)
#
# for order in orders:
#     trading_client.cancel_order_by_id(str(order.id))

# trading_client.close_position(
#     symbol_or_asset_id = 'NVDA',
#     close_options = ClosePositionRequest(
#         qty = "1",
#     )
# )

# limit_order_data = LimitOrderRequest(
#                                     symbol='NVDA',
#                                     qty=1,
#                                     limit_price=170,
#                                     side=OrderSide.BUY,
#                                     type=OrderType.LIMIT,
#                                     time_in_force=TimeInForce.DAY)
#
# limit_order = trading_client.submit_order(order_data=limit_order_data)

# search for crypto assets
# search_params = GetAssetsRequest(asset_class=AssetClass.US_EQUITY)
#
# assets = trading_client.get_all_assets(search_params)
#
# print(assets)
#
#
# # preparing orders
# # market_order_data = MarketOrderRequest(
# #                     symbol="SPY",
# #                     qty=0.023,
# #                     side=OrderSide.BUY,
# #                     time_in_force=TimeInForce.DAY
# #                     )
#
# # limit_order_data = LimitOrderRequest(
# #                         symbol="AAPL",
# #                         limit_price=210,
# #                         qty=601,
# #                         side=OrderSide.SELL,
# #                         time_in_force=TimeInForce.DAY
# #                     )
# #
# #
# # req = LimitOrderRequest(
# #                     symbol = 'AAPL',
# #                     limit_price=209,
# #                     qty = 1,
# #                     side = OrderSide.BUY,
# #                     time_in_force = TimeInForce.DAY,
# #                     order_class = OrderClass.BRACKET,
# #                     take_profit = TakeProfitRequest(limit_price=600),
# #                     stop_loss = StopLossRequest(stop_price=150))
#
#
# # limit_order = trading_client.submit_order(order_data=req)
# resist = 166.02
# close = 164.65
# # place the order
# trade_client = TradingClient('PKIY6QW5KN7LAQ8BKRRZ',
#                                   'za8w8gjyhg7nFLy3eQgEMbZgtODc3QUnswp2jc5V', paper=True)
#
# stop_loss = round(resist * param["stop_loss"], 2) #PARAM
#
# price = round(close * param["price"],2)  # PARAM
#
# take_profit = round(price * param["take_profit"],2)  # PARAM
#
# quantity = math.floor(float(trade_client.get_account().cash) / price)
#
# # do the buy
# limit_order_data = LimitOrderRequest(
#                         symbol="NVDA",
#                         limit_price=price,
#                         qty=1,
#                         side=OrderSide.BUY,
#                         time_in_force=TimeInForce.GTC,
#                         order_class=OrderClass.BRACKET,
#                         take_profit=TakeProfitRequest(limit_price=take_profit),
#                         stop_loss=StopLossRequest(stop_price=stop_loss))
#
# # print(limit_order_data)
# #
# # # place the order
# trade_client = TradingClient('PKIY6QW5KN7LAQ8BKRRZ',
#                                   'za8w8gjyhg7nFLy3eQgEMbZgtODc3QUnswp2jc5V', paper=True)
# # limit_order = trade_client.submit_order(order_data=limit_order_data)
# # print(limit_order)
# #
# cancel_statuses = trading_client.cancel_orders()
# curr_symbol = 'NVDA'
#
# # da = [int(x) for x in datetime.now().strftime("%Y %m %d %H %M").split(" ")]
# # da[3] += 3
# # print(da)
#
#
# get_stock_price = StockBarsRequest(symbol_or_symbols=[curr_symbol],
#                                    timeframe=TimeFrame.Minute)
# # #
# get_stock_price_data = hist_data_client.get_stock_bars(get_stock_price)
# #
# print(get_stock_price_data[curr_symbol])
#
#
# latest_bar_request = StockLatestBarRequest(symbol_or_symbols=[curr_symbol])
#
# # while(True):
# # latest_bar_data = hist_data_client.get_stock_latest_bar(latest_bar_request)

# #
# # print(latest_bar_data)
# #     time.sleep(30)
#
#
# # Bar data from a day
# # day_bar_request = StockBarsRequest(symbol_or_symbols=[curr_symbol],
# #                                    timeframe=TimeFrame.Minute
# #                                    )
# # day_bar_data = hist_data_client.get_stock_bars(day_bar_request)
#
#
# # while(True):
# #     latest_bar_data = hist_data_client.get_stock_latest_bar(latest_bar_request)
# #     print(type(latest_bar_data))
# #     time.sleep(60)
#
#
# # latest_trade_request = StockLatestTradeRequest(symbol_or_symbols=[curr_symbol])
# # latest_trade_data = hist_data_client.get_stock_latest_trade(latest_trade_request)
# #
# # latest_quote_request = StockLatestQuoteRequest(symbol_or_symbols=[curr_symbol])
# # latest_quote_data = hist_data_client.get_stock_latest_quote(latest_quote_request)
# #
# # snapshot_request = StockSnapshotRequest(symbol_or_symbols=[curr_symbol],
# #                                         start=datetime.now())
# # snapshot_data = hist_data_client.get_stock_snapshot(snapshot_request)
#
# # print(snapshot_data)
# #
# # news_request = NewsRequest(symbols=curr_symbol,
# #                            start=datetime(2025,7,1),
# #                            end=datetime(2025,7,2))
# #
# # news_data = news_data_client.get_news(news_request)
#
# # print(news_data)
#
# # print(day_bar_data["ENGS"], len(day_bar_data["ENGS"]))
#
# # Get the dataframe for all highest price in list
# # p_high_df = pd.DataFrame([x.high for x in day_bar_data[curr_symbol]])
# # p_low_df = pd.DataFrame([x.low for x in day_bar_data[curr_symbol]])
# # high_np = np.array([x.high for x in day_bar_data[curr_symbol]][:10])
# # low_np = np.array([x.low for x in day_bar_data[curr_symbol]][:10])
# #
# # test_high = np.array([1,2,3,4,5])
# # test_low = np.array([5,4,3,2,1])
# # print(pattern_detection(test_high, test_low))
#
#
#
# # print(high_np)
# # # print(low_np)
# #
# # print(pattern_detection(high_np,low_np))
#
#
#
# # # print(latest_bar_data.get("AAPL").high)
# #
# # print(latest_trade_data)
# # #
# # print(latest_quote_data)
#
# # print(snapshot_data)
#
# # H = snapshot_data.get(curr_symbol).daily_bar.high
# # L = snapshot_data.get(curr_symbol).daily_bar.low
# # C = snapshot_data.get(curr_symbol).daily_bar.close
# #
# # PP = (H + L + C)/3
# #
# # S1 = (PP * 2) - H
# # S2 = PP - H - L
# #
# # R1 = (PP * 2) - L
# # R2 = PP + H - L
#
# # print(PP, S1, R1, S2, R2)
#
# # print(news_data)
#
# # print(trading_client.get_all_positions())
#
# # async handler
# # async def quote_data_handler(data):
# #     # quote data will arrive here
# #     print(data)
# #
# # wss_client.subscribe_quotes(quote_data_handler, curr_symbol)
#
# # wss_client.run()
#
#
# """
# calculate resistance/support lines algorithm:
# """
# # high_nv = [x.high for x in day_bar_data[curr_symbol]][:10]
# # low_nv = [x.low for x in day_bar_data[curr_symbol]][:10]
# #
# # slope1, inter1,_ = calculate_slope(high_np)
# # slope2, inter2,_ = calculate_slope(low_np)
# #
# # x = np.linspace(0,10,100)
# # y = slope2*x + (min(low_nv)-slope2*low_nv.index(min(low_nv)))
# # y_2 = slope1*x + (max(high_nv)-slope1*high_nv.index(max(high_nv)))
# # x_1 = np.arange(len(high_np))
# # y_1 = high_np
# # x_3 = np.arange(len(low_np))
# # y_3 = low_np
# # plt.plot(x, y, '-r', label='y=2x+1')
# # plt.plot(x_1, y_1, 'ob')
# # plt.plot(x,y_2,'-g')
# # plt.plot(x_3, y_3, 'oy')
# # plt.title('Graph of y=2x+1')
# # plt.xlabel('x', color='#1C2833')
# # plt.ylabel('y', color='#1C2833')
# # plt.legend(loc='upper left')
# # plt.grid()
# # plt.show()
#
#
# # test = " test "
# # print(test)
# # print(test.strip(" "))

# import datetime as dt
#
# MARKET_OPEN_TIME = dt.time(9, 30, 0)  # 9:30 AM (24-hour format) PARAM
# MARKET_CLOSE_TIME = dt.time(16, 0, 0)  # 4:00 PM (24-hour format) PARAM
# PRE_MIDNIGHT = dt.time(23, 59, 59)
# POST_MIDNIGHT = dt.time(0, 0, 0)
#
# if  MARKET_CLOSE_TIME < dt.datetime.now().time() < PRE_MIDNIGHT \
#         or POST_MIDNIGHT < dt.datetime.now().time() < MARKET_OPEN_TIME:
#     print("reached here")
#     print()