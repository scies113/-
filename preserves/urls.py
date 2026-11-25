"""Маршрутизация приложения preserves."""

from django.urls import path, re_path

from . import views

app_name = 'preserves'

urlpatterns = [
    path('', views.preserve_list, name='list'),
    path('<int:preserve_id>/', views.preserve_detail, name='detail'),
    path('new/', views.preserve_create, name='create'),
    path('<int:preserve_id>/edit/', views.preserve_update, name='update'),
    path('products/', views.product_list, name='products'),
    re_path(
        r"^recipe/(?P<slug>[-\w]+)/$",
        views.preserve_detail,
        name="detail_by_slug",
    ),
]
