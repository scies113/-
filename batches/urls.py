"""Маршрутизация приложения batches."""

from django.urls import path

from . import views

app_name = 'batches'

urlpatterns = [
    path('', views.batch_list, name='list'),
    path('<int:batch_id>/', views.batch_detail, name='detail'),
    path('search/', views.batch_search, name='search'),
    path('statistics/', views.batch_statistics, name='statistics'),
]
