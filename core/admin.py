# core/admin.py
from django.contrib import admin
from .models import Client, Order, Material

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'company', 'is_active' , 'avatar')
    search_fields = ('name', 'email', 'company')
    list_filter = ('is_active', 'company')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'client', 'created_at', 'status']  # ✅ was 'order_date'
    list_filter = ['created_at', 'status']  # ✅ was 'order_date'
    search_fields = ['order_id', 'client__name']

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'threshold', 'unit' , 'vendor')
    
