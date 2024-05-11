from django.db import models

# Create your models here.
class StockData(models.Model):
    # db column = [stock_id, open, high, low, close, volume, date]
    stock_id = models.CharField(max_length=10)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()
    date = models.DateField()