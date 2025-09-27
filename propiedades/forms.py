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
                'placeholder': 'Ingrese el título de la propiedad',
                'pattern': '^.{5,100}$',
                'title': 'El título debe tener entre 5 y 100 caracteres',
                'required': True
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describa la propiedad en detalle',
                'pattern': '^.{10,1000}$',
                'title': 'La descripción debe tener entre 10 y 1000 caracteres',
                'required': True
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '1',
                'max': '999999999',
                'placeholder': '0.00',
                'title': 'El precio debe ser mayor a 0 y menor a 999,999,999',
                'required': True
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'operacion': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa de la propiedad',
                'pattern': '^.{5,200}$',
                'title': 'La ubicación debe tener entre 5 y 200 caracteres',
                'required': True
            }),
            'metros_cuadrados': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10000',
                'placeholder': 'Metros cuadrados',
                'title': 'Los metros cuadrados deben estar entre 1 y 10,000',
                'required': True
            }),
            'habitaciones': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '20',
                'placeholder': 'Número de habitaciones',
                'title': 'Las habitaciones deben estar entre 0 y 20',
                'required': True
            }),
            'banos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '10',
                'placeholder': 'Número de baños',
                'title': 'Los baños deben estar entre 0 y 10',
                'required': True
            }),
            'imagen_principal': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png,image/gif,image/webp',
                'title': 'Solo se permiten archivos de imagen (JPEG, PNG, GIF, WebP)',
                'required': True
            }),
            'imagen_secundaria': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png,image/gif,image/webp',
                'title': 'Solo se permiten archivos de imagen (JPEG, PNG, GIF, WebP)'
            }),
            'amenidades': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'latitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0000001',
                'min': '-90',
                'max': '90',
                'placeholder': 'Ej: -38.9516',
                'title': 'La latitud debe estar entre -90 y 90 grados'
            }),
            'longitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0000001',
                'min': '-180',
                'max': '180',
                'placeholder': 'Ej: -68.0591',
                'title': 'La longitud debe estar entre -180 y 180 grados'
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
    
    def clean_titulo(self):
        """Validar el título de la propiedad"""
        titulo = self.cleaned_data.get('titulo')
        if titulo:
            if len(titulo) < 5:
                raise forms.ValidationError('El título debe tener al menos 5 caracteres.')
            elif len(titulo) > 100:
                raise forms.ValidationError('El título no puede tener más de 100 caracteres.')
        return titulo
    
    def clean_descripcion(self):
        """Validar la descripción de la propiedad"""
        descripcion = self.cleaned_data.get('descripcion')
        if descripcion:
            if len(descripcion) < 10:
                raise forms.ValidationError('La descripción debe tener al menos 10 caracteres.')
            elif len(descripcion) > 1000:
                raise forms.ValidationError('La descripción no puede tener más de 1000 caracteres.')
        return descripcion
    
    def clean_precio(self):
        """Validar que el precio sea mayor a 0"""
        precio = self.cleaned_data.get('precio')
        if precio:
            if precio <= 0:
                raise forms.ValidationError('El precio debe ser mayor a 0.')
            elif precio > 999999999:
                raise forms.ValidationError('El precio no puede ser mayor a 999,999,999.')
        return precio
    
    def clean_ubicacion(self):
        """Validar la ubicación de la propiedad"""
        ubicacion = self.cleaned_data.get('ubicacion')
        if ubicacion:
            if len(ubicacion) < 5:
                raise forms.ValidationError('La ubicación debe tener al menos 5 caracteres.')
            elif len(ubicacion) > 200:
                raise forms.ValidationError('La ubicación no puede tener más de 200 caracteres.')
        return ubicacion
    
    def clean_metros_cuadrados(self):
        """Validar que los metros cuadrados sean mayor a 0"""
        metros = self.cleaned_data.get('metros_cuadrados')
        if metros:
            if metros <= 0:
                raise forms.ValidationError('Los metros cuadrados deben ser mayor a 0.')
            elif metros > 10000:
                raise forms.ValidationError('Los metros cuadrados no pueden ser mayor a 10,000.')
        return metros
    
    def clean_habitaciones(self):
        """Validar el número de habitaciones"""
        habitaciones = self.cleaned_data.get('habitaciones')
        if habitaciones is not None:
            if habitaciones < 0:
                raise forms.ValidationError('Las habitaciones no pueden ser negativas.')
            elif habitaciones > 20:
                raise forms.ValidationError('Las habitaciones no pueden ser mayor a 20.')
        return habitaciones
    
    def clean_banos(self):
        """Validar el número de baños"""
        banos = self.cleaned_data.get('banos')
        if banos is not None:
            if banos < 0:
                raise forms.ValidationError('Los baños no pueden ser negativos.')
            elif banos > 10:
                raise forms.ValidationError('Los baños no pueden ser mayor a 10.')
        return banos
    
    def clean_imagen_principal(self):
        """Validar la imagen principal"""
        imagen = self.cleaned_data.get('imagen_principal')
        if imagen:
            # Validar tipo de archivo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if imagen.content_type not in allowed_types:
                raise forms.ValidationError('Solo se permiten archivos de imagen (JPEG, PNG, GIF, WebP).')
            
            # Validar tamaño (5MB máximo)
            if imagen.size > 5 * 1024 * 1024:
                raise forms.ValidationError('La imagen debe ser menor a 5MB.')
        return imagen
    
    def clean_imagen_secundaria(self):
        """Validar la imagen secundaria"""
        imagen = self.cleaned_data.get('imagen_secundaria')
        if imagen:
            # Validar tipo de archivo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if imagen.content_type not in allowed_types:
                raise forms.ValidationError('Solo se permiten archivos de imagen (JPEG, PNG, GIF, WebP).')
            
            # Validar tamaño (5MB máximo)
            if imagen.size > 5 * 1024 * 1024:
                raise forms.ValidationError('La imagen debe ser menor a 5MB.')
        return imagen
    
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
