from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import InvestmentForm, ReturnCalculatorForm
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

def get_data(ticker, stt, edd):
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
            data = get_data(ticker, start_date, end_date)
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

# def stock_detail(request, ticker):
#     # 获取股票的最新日期、收盘价和成交量
#     latest_data = StockData.objects.filter(Ticker=ticker).latest('Date')
#     # 将数据传递给模板
#     return render(request, 'investment/stock_list/stock_detail.html', {
#         'ticker': ticker,
#         'latest_date': latest_data.Date,
#         'latest_close': latest_data.Close,
#         'latest_volume': latest_data.Volume
#     })

def stock_detail(request, ticker):
    # 获取股票的最新日期、收盘价和成交量
    latest_data = StockData.objects.filter(Ticker=ticker).latest('Date')
    latest_date = latest_data.Date
    latest_close = latest_data.Close
    latest_volume = latest_data.Volume

    # 获取股票的历史数据
    historical_data = StockData.objects.filter(Ticker=ticker).order_by('Date')

    # 提取日期和收盘价数据
    dates = [data.Date for data in historical_data]
    prices = [data.Close for data in historical_data]

    # 绘制股票走势图
    fig, ax = plt.subplots()
    ax.plot(dates, prices)
    ax.set(xlabel='Date', ylabel='Price', title='Stock Price Trend')
    ax.grid()


    save_folder = 'charts'
    os.makedirs(save_folder, exist_ok=True)

    # 保存图表到本地
    save_path = os.path.join(save_folder, '{}_chart.png'.format(ticker))
    plt.savefig(save_path, format='png')

    # 关闭图表
    plt.close()
    # 将图像转换为 base64 编码的字符串
    with open(save_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')

    # # 将图表转换为图像
    # buffer = io.BytesIO()
    # plt.savefig(buffer, format='png')
    # buffer.seek(0)
    # plt.close()

    # # 将图像转换为 base64 编码的字符串
    # image_png = buffer.getvalue()
    # buffer.close()
    # graphic = urllib.parse.quote(image_png)


    # 将数据传递给模板
    return render(request, 'investment/stock_list/stock_detail.html', {
        'ticker': ticker,
        'latest_date': latest_date,
        'latest_close': latest_close,
        'latest_volume': latest_volume,
        'graphic': image_data  # 将图表的 base64 编码字符串传递给模板
    })

def backtest(request):
    tickers = StockData.objects.values_list('Ticker', flat=True).distinct()
    show_avg_form = False
    if request.method == 'POST':
        backtest_type = request.POST.get('backtest_type')
        if backtest_type == 'avg':
            show_avg_form = True
    return render(request, 'investment/backtest.html', {'tickers': tickers, 'show_avg_form': show_avg_form})