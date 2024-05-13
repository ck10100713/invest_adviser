# import_data.py
import csv
from datetime import datetime


import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invest_adviser.settings')
django.setup()

from investment.models import StockData

def import_stock_data(csv_file_path):
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            ticker = row[0]
            date = datetime.strptime(row[1], '%Y-%m-%d').date()
            open_price = float(row[2])
            high_price = float(row[3])
            low_price = float(row[4])
            close_price = float(row[5])
            volume = int(row[6])
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

# 调用导入函数
import_stock_data('data.csv')
