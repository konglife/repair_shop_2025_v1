# repairs/urls.py
from django.urls import path
from . import views

app_name = 'repairs'

urlpatterns = [
    path('', views.index, name='index'),  # หน้าแรกของแอป inventory
]
