from django import forms
from .models import Propiedad

class PropiedadForm(forms.ModelForm):
    """Formulario para crear y editar propiedades"""
    
    # Campo para múltiples fotos adicionales (usando CharField para URLs)
    fotos_adicionales = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        help_text="Fotos adicionales se manejan por separado"
    )
    
    class Meta:
        model = Propiedad
        fields = [
            'titulo', 'descripcion', 'precio', 'tipo', 'operacion', 
            'estado', 'ubicacion', 'habitaciones', 'banos', 
            'metros_cuadrados', 'imagen_principal', 'imagen_secundaria',
            'amenidades'  # Agregar campo de amenidades
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'operacion': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'habitaciones': forms.NumberInput(attrs={'class': 'form-control'}),
            'banos': forms.NumberInput(attrs={'class': 'form-control'}),
            'metros_cuadrados': forms.NumberInput(attrs={'class': 'form-control'}),
            'imagen_principal': forms.FileInput(attrs={'class': 'form-control'}),
            'imagen_secundaria': forms.FileInput(attrs={'class': 'form-control'}),
            'amenidades': forms.CheckboxSelectMultiple(attrs={'class': 'amenidad-checkbox'})
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
            'imagen_principal': 'Imagen Principal',
            'imagen_secundaria': 'Imagen Secundaria'
        }
        help_texts = {
            'titulo': 'Un título descriptivo y atractivo para la propiedad',
            'descripcion': 'Describe las características, amenidades y detalles importantes',
            'precio': 'Precio en pesos argentinos',
            'operacion': 'Selecciona si la propiedad es para venta, alquiler o alquiler temporal',
            'imagen_principal': 'Imagen principal de la propiedad (formato: JPG, PNG)',
            'imagen_secundaria': 'Imagen secundaria para mostrar en el detalle (formato: JPG, PNG)'
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
    
    def save(self, commit=True):
        """Guardar la propiedad"""
        propiedad = super().save(commit=False)
        
        if commit:
            propiedad.save()
        
        return propiedad
