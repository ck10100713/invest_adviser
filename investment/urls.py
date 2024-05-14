from django.contrib import admin
from django.urls import path, include
from .views import investment, calculate_and_show_results, calculate_dollar_cost_averaging, stock_list

urlpatterns = [
    path('', investment, name='investment'),
    path('calculate/', calculate_and_show_results, name='calculate_view'),
    path('dollar-cost-averaging/', calculate_dollar_cost_averaging, name='dollar_cost_averaging_view'),
    path('stock-list/', stock_list, name='stock_list')
]