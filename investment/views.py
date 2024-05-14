from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import InvestmentForm, ReturnCalculatorForm
from .models import StockData

# Create your views here.
def investment(request):
    return render(request, 'investment/investment.html')

def calculate_returns(request):
    if request.method == 'POST':
        form = ReturnCalculatorForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            months = form.cleaned_data['months']
            rate = form.cleaned_data['rate']
            total_return = amount * ((1 + (rate / 100)) ** months)
            return render(request, 'investment/result.html', {
                'total_return': total_return,
                'form': form
            })
    else:
        form = ReturnCalculatorForm()

    return render(request, 'investment/calculate.html', {'form': form})

def calculate_and_show_results(request):
    form = ReturnCalculatorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        amount = form.cleaned_data['amount']
        months = form.cleaned_data['months']
        rate = form.cleaned_data['rate']
        total_return = amount * ((1 + (rate / 100)) ** months)
        context = {
            'form': form,
            'total_return': total_return,
            'result': True
        }
    else:
        context = {'form': form, 'result': False}

    return render(request, 'investment/calculate_and_result.html', context)

def calculate_dollar_cost_averaging(request):
    form = ReturnCalculatorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        amount = form.cleaned_data['amount']
        months = form.cleaned_data['months']
        rate = form.cleaned_data['rate']
        total_return = (amount * (((1 + (rate / 100)) ** (months)) - 1))/(rate / 100)
        context = {
            'form': form,
            'total_return': total_return,
            'result': True
        }
    else:
        context = {'form': form, 'result': False}

    return render(request, 'investment/calculate_and_result.html', context)

def stock_list(request):
    ticker_list = StockData.objects.values_list('Ticker', flat=True).distinct()
    return render(request, 'investment/stock_list.html', {'ticker_list': ticker_list})

def stock_detail(request, ticker):
    # 获取股票的最新日期、收盘价和成交量
    latest_data = StockData.objects.filter(Ticker=ticker).latest('Date')
    # 将数据传递给模板
    return render(request, 'investment/stock_list/stock_detail.html', {
        'ticker': ticker,
        'latest_date': latest_data.Date,
        'latest_close': latest_data.Close,
        'latest_volume': latest_data.Volume
    })