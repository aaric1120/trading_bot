import yfinance as yf
from talib import CDLENGULFING,CDLHAMMER,CDLMARUBOZU,CDL3WHITESOLDIERS,CDLCLOSINGMARUBOZU,CDLBELTHOLD
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
    engulfing = CDLENGULFING(OPEN,HIGH,LOW,CLOSE)
    hammer = CDLHAMMER(OPEN,HIGH,LOW,CLOSE)
    marubozu = CDLMARUBOZU(OPEN,HIGH,LOW,CLOSE)
    three_white = CDL3WHITESOLDIERS(OPEN,HIGH,LOW,CLOSE)
    closing_maru = CDLCLOSINGMARUBOZU(OPEN,HIGH,LOW,CLOSE)
    belthold = CDLBELTHOLD(OPEN,HIGH,LOW,CLOSE)

    print((engulfing[-1] + engulfing[-2]) == 0)

    # Print dates where engulfing occurred
    for i in range(len(engulfing)):
        if engulfing[i] != 0:
            print(f"{data.index[i].date()}:{data.index[i].time()} → {'Bullish' if engulfing[i] > 0 else 'Bearish'} Engulfing")

    for i in range(len(hammer)):
        if engulfing[i] != 0:
            print(f"{data.index[i].date()}:{data.index[i].time()} → {'Bullish' if hammer[i] > 0 else 'Bearish'} Hammer")

    for i in range(len(marubozu)):
        if marubozu[i] != 0:
            print(f"{data.index[i].date()}:{data.index[i].time()} → {'Bullish' if marubozu[i] > 0 else 'Bearish'} marubozu")

    for i in range(len(three_white)):
        if three_white[i] != 0:
            print(f"{data.index[i].date()}:{data.index[i].time()} → {'Bullish' if three_white[i] > 0 else 'Bearish'} three_white")

    for i in range(len(closing_maru)):
        if closing_maru[i] != 0:
            print(f"{data.index[i].date()}:{data.index[i].time()} → {'Bullish' if closing_maru[i] > 0 else 'Bearish'} closing_maru")

    for i in range(len(belthold)):
        if belthold[i] != 0:
            print(f"{data.index[i].date()}:{data.index[i].time()} → {'Bullish' if belthold[i] > 0 else 'Bearish'} belthold")



check_candle("NXT")