import yfinance as yf
import talib
import numpy as np


def check_candle(stock):
    # Download Apple stock data
    data = yf.download(stock, period="1d", interval="1m")
    print(data)
    # print(np.array([x[0] for x in data["Open"].values.tolist()], dtype=float))
    OPEN = np.array([x[0] for x in data["Open"].values.tolist()], dtype=float)
    HIGH = np.array([x[0] for x in data["High"].values.tolist()], dtype=float)
    LOW = np.array([x[0] for x in data["Low"].values.tolist()], dtype=float)
    CLOSE = np.array([x[0] for x in data["Close"].values.tolist()], dtype=float)

    # Detect engulfing patterns
    engulfing = talib.CDLENGULFING(OPEN,HIGH,LOW,CLOSE)
    hammer = talib.CDLHAMMER(OPEN,HIGH,LOW,CLOSE)

    print((engulfing[-1] + engulfing[-2]) == 0)

    # Print dates where engulfing occurred
    for i in range(len(engulfing)):
        if engulfing[i] != 0:
            print(f"{data.index[i].date()}:{data.index[i].time()} → {'Bullish' if engulfing[i] > 0 else 'Bearish'} Engulfing")

    for i in range(len(hammer)):
        if engulfing[i] != 0:
            print(f"{data.index[i].date()}:{data.index[i].time()} → {'Bullish' if hammer[i] > 0 else 'Bearish'} Hammer")


check_candle("NXT")