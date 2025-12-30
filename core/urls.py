from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),                                # Main Dashboard
    path('client/', views.client_dashboard, name='client_dashboard'),
    
    # === ORDERS SECTION ===
    # REMOVED THE DUPLICATE: path('order/', ..., name='order')
    
    # Keep this one because views.add_order_for_client redirects to 'order_dashboard'
    path('order/', views.order_dashboard, name='order_dashboard'),      
    
    # This specific path must exist for the "+ Order" button in client dashboard
    path('order/add/<int:client_id>/', views.add_order_for_client, name='add_order_for_client'),
    
    path('inventory/', views.inventory_dashboard, name='inventory_dashboard'),
    path('finance/', views.finance_dashboard, name='finance_dashboard'),
    
    # urls.py
    path('finance/invoice/<int:invoice_id>/', views.view_invoice, name='view_invoice'),
    # urls.py
    path('finance/invoice/<int:invoice_id>/pdf/', views.download_invoice_pdf, name='download_invoice_pdf'),
    
    # API
    path('api/clients/', views.client_search_api, name='client_search_api'),
    
]