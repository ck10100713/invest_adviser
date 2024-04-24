from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def investment(request):
    return render(request, 'investment/investment.html')