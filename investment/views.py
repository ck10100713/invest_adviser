from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import InvestmentForm, ReturnCalculatorForm

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