from django.contrib import admin
from django.urls import path, include
from . import views
# from .views import investment
# from .views import calculate_and_show_results, calculate_dollar_cost_averaging
# from .views import stock_list, stock_detail

urlpatterns = [
    path('', views.investment, name='investment'),
    path('calculate/', views.calculate_and_show_results, name='calculate_view'),
    path('dollar-cost-averaging/', views.calculate_dollar_cost_averaging, name='dollar_cost_averaging_view'),
    path('stock-list/', views.stock_list, name='stock_list'),
    path('stock-detail/<str:ticker>/', views.stock_detail, name='stock_detail'),
]