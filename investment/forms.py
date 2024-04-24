from django import forms
from django.utils.translation import gettext_lazy as _ # 新增

class InvestmentForm(forms.Form):
    name = forms.CharField(label=_('Name'), max_length=100)
    amount = forms.FloatField(label=_('Amount'))
    interest_rate = forms.FloatField(label=_('Interest Rate'))
    duration = forms.IntegerField(label=_('Duration'))
    result = forms.FloatField(label=_('Result'), required=False)
    created_at = forms.DateTimeField(label=_('Created At'), required=False)
    updated_at = forms.DateTimeField(label=_('Updated At'), required=False)
    
    def calculate(self):
        self.result = self.amount * (1 + self.rate / 100 * self.time)
        return self.result
    def __str__(self):
        return f"Investment: {self.amount} for {self.duration} months at {self.interest_rate}%"