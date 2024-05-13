from django.db import models

# Create your models here.
class StockData(models.Model):
    # db column = [stock_id, open, high, low, close, volume, date]
    Ticker = models.CharField(max_length=10)
    Date = models.DateField()
    Open = models.FloatField()
    High = models.FloatField()
    Low = models.FloatField()
    Close = models.FloatField()
    Adj_Close = models.FloatField()
    Volume = models.FloatField()

    def __str__(self):
        return self.Ticker