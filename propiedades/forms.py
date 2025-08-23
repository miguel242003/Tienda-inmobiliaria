from django import forms
from .models import Propiedad

class PropiedadForm(forms.ModelForm):
    """Formulario para crear y editar propiedades"""
    
    class Meta:
        model = Propiedad
        fields = [
            'titulo', 'descripcion', 'precio', 'tipo', 'operacion', 'estado',
            'ubicacion', 'metros_cuadrados', 'habitaciones', 'banos',
            'imagen_principal'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Ej: Casa moderna con jardín'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe las características principales de la propiedad...'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '$ 0',
                'min': '0',
                'step': '1'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select form-select-lg'
            }),
            'operacion': forms.Select(attrs={
                'class': 'form-select form-select-lg'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select form-select-lg'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Ej: Colonia Jardines del Valle, Ciudad de México'
            }),
            'metros_cuadrados': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0'
            }),
            'habitaciones': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0'
            }),
            'banos': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0'
            }),
            'imagen_principal': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'titulo': 'Título de la Propiedad',
            'descripcion': 'Descripción',
            'precio': 'Precio (ARS)',
            'tipo': 'Tipo de Propiedad',
            'operacion': 'Tipo de Operación',
            'estado': 'Estado',
            'ubicacion': 'Ubicación',
            'metros_cuadrados': 'Metros Cuadrados',
            'habitaciones': 'Habitaciones',
            'banos': 'Baños',
            'imagen_principal': 'Imagen Principal'
        }
        help_texts = {
            'titulo': 'Un título descriptivo y atractivo para la propiedad',
            'descripcion': 'Describe las características, amenidades y detalles importantes',
            'precio': 'Precio en pesos argentinos',
            'operacion': 'Selecciona si la propiedad es para venta, alquiler o alquiler temporal',
            'imagen_principal': 'Imagen principal de la propiedad (formato: JPG, PNG)'
        }
    
    def clean_precio(self):
        """Validar que el precio sea positivo"""
        precio = self.cleaned_data.get('precio')
        if precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0.')
        return precio
    
    def clean_metros_cuadrados(self):
        """Validar que los metros cuadrados sean positivos"""
        metros = self.cleaned_data.get('metros_cuadrados')
        if metros <= 0:
            raise forms.ValidationError('Los metros cuadrados deben ser mayores a 0.')
        return metros
