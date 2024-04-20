from django.db import models

# Create your models here.
class Investment(models.Model):
    name = models.CharField(max_length=100)
    amount = models.FloatField()
    interest_rate = models.FloatField()
    duration = models.IntegerField()
    result = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate(self):
        self.result = self.amount * (1 + self.rate / 100 * self.time)
        return self.result
    
    # def __str__(self):
    #     return self.name
    def __str__(self):
        return f"Investment: {self.amount} for {self.duration} months at {self.interest_rate}%"