import csv, sys, os

path = os.path.join(os.path.dirname(__file__), 'data.csv')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import django
django.setup()
from investment.models import StockData
data = csv.reader(open(path), delimiter=',')
for row in data:
    if row[0] != 'stock_id':
        stock = StockData()
        stock.Ticker = row[0]
        stock.Date = row[1]
        stock.Open = row[2]
        stock.High = row[3]
        stock.Low = row[4]
        stock.Close = row[5]
        stock.Adj_Close = row[6]
        stock.Volume = row[7]
        stock.save()