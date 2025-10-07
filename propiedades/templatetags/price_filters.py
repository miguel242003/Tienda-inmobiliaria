from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def precio_argentino(value):
    """
    Formatea un precio en formato argentino: 110.000 en lugar de 110,000.00
    """
    if value is None:
        return ""
    
    try:
        # Convertir a float si es string
        if isinstance(value, str):
            value = float(value.replace(',', '.'))
        
        # Formatear con punto como separador de miles
        formatted = f"{value:,.0f}".replace(',', '.')
        return f"${formatted}"
    except (ValueError, TypeError):
        return f"${value}"

@register.filter
def precio_argentino_decimal(value):
    """
    Formatea un precio en formato argentino con decimales: 110.000,50
    """
    if value is None:
        return ""
    
    try:
        # Convertir a float si es string
        if isinstance(value, str):
            value = float(value.replace(',', '.'))
        
        # Formatear con punto como separador de miles y coma como decimal
        formatted = f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return f"${formatted}"
    except (ValueError, TypeError):
        return f"${value}"
