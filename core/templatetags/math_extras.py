# D:\project1\core\templatetags\math_extras.py
from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply two numbers (supports Decimal and strings)"""
    try:
        return Decimal(value) * Decimal(arg)
    except (TypeError, ValueError):
        return Decimal('0')