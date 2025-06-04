# inventory/urls.py
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.index, name='index'),  # หน้าแรกของแอป inventory
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('purchases/', views.purchase_list, name='purchase_list'),
    path('purchases/add/', views.add_purchase, name='add_purchase'),
]
