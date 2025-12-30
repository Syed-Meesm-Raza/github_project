# core/forms.py
from django import forms
from .models import Client
from .models import Order

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'company', 'avatar' , 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'client@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['fabric_type', 'quantity', 'due_date', 'status', 'payment']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'payment': forms.NumberInput(attrs={'step': '0.01'}),
        }