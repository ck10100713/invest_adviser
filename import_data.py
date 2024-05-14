import pandas as pd
# import talib
# import numpy as np
# import matplotlib.pyplot as plt
import yfinance as yf
import sys
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invest_adviser.settings')
django.setup()

from investment.models import StockData

def get_data(ticker):
    data = yf.download(ticker, start='2024-04-01', end='2024-05-01')
    data['Ticker'] = ticker
    data = data.reset_index()
    data['Date'] = pd.to_datetime(data['Date'])
    data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')
    data = data.reindex(columns=['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    return data

def import_stock_data(ticker):
    data = get_data(ticker)
    for item in data.itertuples():
        ticker = item.Ticker
        date = item.Date
        open_price = float(item.Open)
        high_price = float(item.High)
        low_price = float(item.Low)
        close_price = float(item.Close)
        volume = int(item.Volume)
        stock_data = StockData.objects.create(
            Ticker=ticker,
            Date=date,
            Open=open_price,
            High=high_price,
            Low=low_price,
            Close=close_price,
            Volume=volume
        )
        stock_data.save()


if __name__ == '__main__':
    ticker = sys.argv[1]
    print("Importing data for {}".format(ticker))
    try:
        import_stock_data(ticker)
        print("Data for {} has been imported".format(ticker))
    except Exception as e:
        print("Error importing data for {}: {}".format(ticker, e))