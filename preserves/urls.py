"""Маршрутизация приложения preserves."""

from django.urls import path

from . import views

app_name = 'preserves'

urlpatterns = [
    path('', views.preserve_list, name='list'),
    path('<int:preserve_id>/', views.preserve_detail, name='detail'),
    path('products/', views.product_list, name='products'),
]
