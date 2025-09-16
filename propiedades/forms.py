from django import forms
from .models import Propiedad, Resena

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

class ResenaForm(forms.ModelForm):
    """Formulario para crear reseñas de propiedades"""
    
    class Meta:
        model = Resena
        fields = [
            'nombre_usuario', 'email_usuario', 'telefono_usuario',
            'calificacion', 'titulo', 'comentario'
        ]
        widgets = {
            'nombre_usuario': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Tu nombre completo'
            }),
            'email_usuario': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'tu@email.com'
            }),
            'telefono_usuario': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': '+54 9 11 1234-5678 (opcional)'
            }),
            'calificacion': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'min': '1',
                'max': '5',
                'value': '5'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Título de tu reseña'
            }),
            'comentario': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 4,
                'placeholder': 'Comparte tu experiencia con esta propiedad...'
            })
        }
        labels = {
            'nombre_usuario': 'Nombre Completo',
            'email_usuario': 'Correo Electrónico',
            'telefono_usuario': 'Teléfono (Opcional)',
            'calificacion': 'Calificación',
            'titulo': 'Título de la Reseña',
            'comentario': 'Comentario'
        }
        help_texts = {
            'nombre_usuario': 'Tu nombre completo aparecerá en la reseña',
            'email_usuario': 'Tu email no será visible públicamente',
            'telefono_usuario': 'Opcional, para contacto directo',
            'calificacion': 'Califica del 1 al 5 estrellas',
            'titulo': 'Un título descriptivo para tu reseña',
            'comentario': 'Describe tu experiencia con la propiedad'
        }
    
    def clean_calificacion(self):
        """Validar que la calificación esté entre 1 y 5"""
        calificacion = self.cleaned_data.get('calificacion')
        if calificacion < 1 or calificacion > 5:
            raise forms.ValidationError('La calificación debe estar entre 1 y 5 estrellas.')
        return calificacion
    
    def clean_comentario(self):
        """Validar que el comentario tenga al menos 10 caracteres"""
        comentario = self.cleaned_data.get('comentario')
        if len(comentario.strip()) < 10:
            raise forms.ValidationError('El comentario debe tener al menos 10 caracteres.')
        return comentario
    
    def clean_nombre_usuario(self):
        """Validar que el nombre no esté vacío"""
        nombre = self.cleaned_data.get('nombre_usuario')
        if len(nombre.strip()) < 2:
            raise forms.ValidationError('El nombre debe tener al menos 2 caracteres.')
        return nombre.strip()
