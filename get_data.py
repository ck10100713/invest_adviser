import pandas as pd
# import talib
# import numpy as np
# import matplotlib.pyplot as plt
import yfinance as yf
from investment.models import StockData
import sys

def get_data(ticker):
    data = yf.download(ticker, start='2024-04-01', end='2024-05-01')
    data['ticker'] = ticker
    data['date'] = data.index.date
    data['date'] = pd.to_datetime(data['date'])
    data = data.reindex(columns=['ticker', 'date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
    data = data.reset_index()
    return data

def import_data(ticker):
    data = get_data(ticker)
    data = data.to_dict(orient='records')
    StockData.objects.bulk_create([StockData(**vals) for vals in data])

if __name__ == '__main__':
    ticker = sys.argv[1]
    print(f"Importing data for {ticker}")
    try:
        # import_data(ticker)
        # data = get_data(ticker)
        print(f"Data for {ticker} has been imported")
    except Exception as e:
        print(f"Error importing data for {ticker}: {e}")