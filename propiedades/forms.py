from django import forms
from .models import Propiedad, Amenidad

class PropiedadForm(forms.ModelForm):
    """Formulario para crear y editar propiedades"""
    
    class Meta:
        model = Propiedad
        fields = [
            'titulo', 'descripcion', 'precio', 'tipo', 'operacion', 'estado',
            'ubicacion', 'metros_cuadrados', 'habitaciones', 'banos',
            'imagen_principal', 'imagen_secundaria', 'amenidades',
            'latitud', 'longitud'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el título de la propiedad'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describa la propiedad en detalle'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'operacion': forms.Select(attrs={
                'class': 'form-control'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa de la propiedad'
            }),
            'metros_cuadrados': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Metros cuadrados'
            }),
            'habitaciones': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Número de habitaciones'
            }),
            'banos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Número de baños'
            }),
            'imagen_principal': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'imagen_secundaria': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'amenidades': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'latitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0000001',
                'placeholder': 'Ej: -38.9516'
            }),
            'longitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0000001',
                'placeholder': 'Ej: -68.0591'
            }),
        }
        labels = {
            'titulo': 'Título de la Propiedad',
            'descripcion': 'Descripción',
            'precio': 'Precio',
            'tipo': 'Tipo de Propiedad',
            'operacion': 'Tipo de Operación',
            'estado': 'Estado',
            'ubicacion': 'Ubicación',
            'metros_cuadrados': 'Metros Cuadrados',
            'habitaciones': 'Habitaciones',
            'banos': 'Baños',
            'imagen_principal': 'Imagen Principal',
            'imagen_secundaria': 'Imagen Secundaria',
            'amenidades': 'Amenidades',
            'latitud': 'Latitud',
            'longitud': 'Longitud',
        }
        help_texts = {
            'latitud': 'Coordenada de latitud para mostrar en el mapa (ej: -38.9516)',
            'longitud': 'Coordenada de longitud para mostrar en el mapa (ej: -68.0591)',
            'amenidades': 'Seleccione las amenidades que incluye la propiedad',
        }
    
    def clean_precio(self):
        """Validar que el precio sea mayor a 0"""
        precio = self.cleaned_data.get('precio')
        if precio and precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0.')
        return precio
    
    def clean_metros_cuadrados(self):
        """Validar que los metros cuadrados sean mayor a 0"""
        metros = self.cleaned_data.get('metros_cuadrados')
        if metros and metros <= 0:
            raise forms.ValidationError('Los metros cuadrados deben ser mayor a 0.')
        return metros
    
    def clean_latitud(self):
        """Validar que la latitud esté en el rango correcto"""
        latitud = self.cleaned_data.get('latitud')
        if latitud is not None:
            if latitud < -90 or latitud > 90:
                raise forms.ValidationError('La latitud debe estar entre -90 y 90 grados.')
        return latitud
    
    def clean_longitud(self):
        """Validar que la longitud esté en el rango correcto"""
        longitud = self.cleaned_data.get('longitud')
        if longitud is not None:
            if longitud < -180 or longitud > 180:
                raise forms.ValidationError('La longitud debe estar entre -180 y 180 grados.')
        return longitud
