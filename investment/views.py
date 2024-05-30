from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import InvestmentForm, ReturnCalculatorForm, AvgStragetyForm
from .models import StockData
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import urllib
from django.http import HttpResponse
import os
import base64
import datetime as dt
import pandas as pd
import yfinance as yf
from io import BytesIO, StringIO

plt_size = (8,6)

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

def get_data_from_yf(ticker, stt, edd):
    ticker = ticker.upper()
    data = yf.download(ticker, start = stt, end = edd)
    data['Ticker'] = ticker
    data = data.reset_index()
    data['Date'] = pd.to_datetime(data['Date'])
    data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')
    data = data.reindex(columns=['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    return data

def import_data_view(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        try:
            data = get_data_from_yf(ticker, start_date, end_date)
            for item in data.itertuples():
                ticker = item.Ticker
                date = item.Date
                open_price = float(item.Open)
                high_price = float(item.High)
                low_price = float(item.Low)
                close_price = float(item.Close)
                volume = int(item.Volume)
                if not StockData.objects.filter(Ticker=ticker, Date=date).exists():
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
            msg = 'Success: Data for {} from {} to {} has been imported'.format(ticker, start_date, end_date)
        except Exception as e:
            msg = "Error importing data for {}: {}".format(ticker, e)
        return HttpResponse(msg)
    return render(request, 'investment/import_data.html')

def stock_list(request):
    ticker_list = StockData.objects.values_list('Ticker', flat=True).distinct()
    return render(request, 'investment/stock_list.html', {'ticker_list': ticker_list})

def stock_detail(request, ticker):
    latest_data = StockData.objects.filter(Ticker=ticker).latest('Date')
    latest_date = latest_data.Date
    latest_close = latest_data.Close
    latest_volume = latest_data.Volume

    historical_data = StockData.objects.filter(Ticker=ticker).order_by('Date')

    dates = [data.Date for data in historical_data]
    prices = [data.Close for data in historical_data]

    fig, ax = plt.subplots()
    ax.plot(dates, prices)
    ax.set(xlabel='Date', ylabel='Price', title='Stock Price Trend')
    ax.grid()

    # another way to save the chart
    # save_folder = 'charts'
    # os.makedirs(save_folder, exist_ok=True)

    # save_path = os.path.join(save_folder, '{}_chart.png'.format(ticker))
    # plt.savefig(save_path, format='png')

    # plt.close()
    # with open(save_path, "rb") as image_file:
    #     image_data = base64.b64encode(image_file.read()).decode('utf-8')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    image_data = f"data:image/png;base64,{image_base64}"

    return render(request, 'investment/stock_list/stock_detail.html', {
        'ticker': ticker,
        'latest_date': latest_date,
        'latest_close': latest_close,
        'latest_volume': latest_volume,
        'graphic': image_data
    })

def backtest(request):
    show_avg_form = False
    if request.method == 'POST':
        form = AvgStragetyForm(request.POST)
        backtest_type = request.POST.get('backtest_type')
        if backtest_type == 'avg':
            show_avg_form = True
        if form.is_valid():
            ticker = form.cleaned_data['ticker']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            days = form.cleaned_data['days']
            amount = form.cleaned_data['amount']
            # data = get_data_from_db(ticker, start_date, end_date)
            strategy = [backtest_type, ticker, start_date, end_date, [days, amount]]
            return_data = cal_strategry_return(strategy)
            return backtest_results(request, strategy, return_data)
    else:
        form = AvgStragetyForm()
    return render(request, 'investment/backtest/backtest_page.html', {
        'form': form,
        'show_avg_form': show_avg_form
    })

def backtest_results(request, strategy, return_data):
    ticker = return_data['Ticker'][0]
    strategy = strategy[0]
    strategy_parameters = strategy[2]
    total_cost = return_data['cumulative_cost'].iloc[-1]
    total_revenue = return_data['amount'].iloc[-1]
    price_movement_image = generate_price_movement_image(return_data)
    cost_revenue_image = generate_cost_revenue_image(return_data)

    return render(request, 'investment/backtest/backtest_results.html', {'ticker': ticker, 'strategy': strategy, 'strategy_parameters': strategy_parameters,
                'total_cost': total_cost, 'total_revenue': total_revenue,
                'price_movement_image': price_movement_image, 'cost_revenue_image': cost_revenue_image})
def generate_price_movement_image(data):
    plt.figure(figsize=plt_size)
    plt.plot(data['Date'], data['Close'], label='Close Price', color='black')
    plt.scatter(data[data['shares'] > 0]['Date'], data[data['shares'] > 0]['Close'], marker='^', color='green', label='Buy Signal', s=50)
    # plt.scatter(filtered_data[filtered_data['shares'] == 0]['Date'], filtered_data[filtered_data['shares'] == 0]['Close'], marker='v', color='red')
    plt.title('Dollar Cost Averaging')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.legend()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    image_data = f"data:image/png;base64,{image_base64}"
    return image_data

def generate_cost_revenue_image(data):
    plt.figure(figsize=plt_size)
    plt.plot(data['Date'], data['cumulative_cost'], label='Cumulative Cost', color='blue')
    plt.plot(data['Date'], data['amount'], label='Amount', color='red')
    plt.title('Dollar Cost Averaging')
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.legend()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    image_data = f"data:image/png;base64,{image_base64}"
    return image_data

def get_data_from_db(ticker, start_date = None, end_date = None):
    ticker = ticker.upper()
    data = StockData.objects.filter(Ticker=ticker).order_by('Date')
    data = pd.DataFrame(list(data.values()))
    data['Date'] = pd.to_datetime(data['Date'])
    data['Year'] = data['Date'].dt.year
    data['Month'] = data['Date'].dt.month
    data['Day'] = data['Date'].dt.day
    data = data.reindex(columns=['Ticker', 'Date', 'Year', 'Month', 'Day', 'Open', 'High', 'Low', 'Close', 'Volume'])
    return data

def cal_avg_return(ticker, start_date = None, end_date = None,days, amount):
    data = get_data_from_db(ticker, start_date, end_date)
    choosen_day = days
    monthly_amount = amount
    filtered_data = data.copy()
    filtered_data['shares'] = 0
    filtered_data.loc[filtered_data['Day'] == choosen_day, 'shares'] = monthly_amount // (filtered_data.loc[filtered_data['Day'] == choosen_day, 'Close'])
    filtered_data['cost'] = filtered_data['shares'] * filtered_data['Close']
    filtered_data['cumulative_shares'] = filtered_data['shares'].cumsum()
    filtered_data['amount'] = filtered_data['cumulative_shares'] * filtered_data['Close']
    filtered_data['cumulative_cost'] = filtered_data['cost'].cumsum()
    filtered_data['return'] = filtered_data['amount'] - filtered_data['cumulative_cost']
    return filtered_data

def cal_strategry_return(strategy):
    strategy_type = strategy[0]
    ticker = strategy[1]
    start_date = strategy[2]
    end_date = strategy[3]
    if strategy_type == 'avg':
        days = strategy[4][0]
        amount = strategy[4][1]
        return cal_avg_return(ticker, start_date, end_date, days, amount)