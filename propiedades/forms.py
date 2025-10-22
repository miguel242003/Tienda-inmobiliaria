from django import forms
from .models import Propiedad, Amenidad, Resena

class PropiedadForm(forms.ModelForm):
    """Formulario para crear y editar propiedades"""
    
    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)
        
        # Si es edición, hacer algunos campos opcionales
        if self.is_edit:
            self.fields['imagen_principal'].required = False
            self.fields['imagen_secundaria'].required = False
            self.fields['latitud'].required = False
            self.fields['longitud'].required = False
            self.fields['ciudad'].required = False
            self.fields['lugares_cercanos'].required = False
    
    class Meta:
        model = Propiedad
        fields = [
            'titulo', 'descripcion', 'precio', 'tipo', 'operacion', 'estado',
            'ubicacion', 'ciudad', 'lugares_cercanos', 'metros_cuadrados', 'habitaciones', 'banos',
            'ambientes', 'balcon', 'imagen_principal', 'imagen_secundaria', 'amenidades',
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
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad donde se encuentra la propiedad',
                'maxlength': '100',
                'title': 'Ciudad de la propiedad',
                'required': True
            }),
            'lugares_cercanos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe los lugares cercanos (centros comerciales, restaurantes, servicios, etc.)',
                'maxlength': '500',
                'title': 'Lugares cercanos a la propiedad',
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
            'ambientes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '30',
                'placeholder': 'Número de ambientes',
                'title': 'Los ambientes deben estar entre 0 y 30',
                'required': True
            }),
            'balcon': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
            'imagen_principal': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png,image/gif,image/webp',
                'title': 'Solo se permiten archivos de imagen (JPEG, PNG, GIF, WebP)',
                'required': False  # No requerido en edición
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
                'step': 'any',
                'min': '-90',
                'max': '90',
                'placeholder': 'Ej: -33.6914783645518',
                'title': 'La latitud debe estar entre -90 y 90 grados',
                'required': False  # No requerido en edición
            }),
            'longitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'min': '-180',
                'max': '180',
                'placeholder': 'Ej: -65.45524318970048',
                'title': 'La longitud debe estar entre -180 y 180 grados',
                'required': False  # No requerido en edición
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
            'ciudad': 'Ciudad',
            'lugares_cercanos': 'Lugares Cercanos',
            'metros_cuadrados': 'Metros Cuadrados',
            'habitaciones': 'Habitaciones',
            'banos': 'Baños',
            'ambientes': 'Ambientes',
            'balcon': 'Tiene Balcón',
            'imagen_principal': 'Imagen Principal',
            'imagen_secundaria': 'Imagen Secundaria',
            'amenidades': 'Amenidades',
            'latitud': 'Latitud',
            'longitud': 'Longitud',
        }
        help_texts = {
            'ciudad': 'Ciudad donde se encuentra la propiedad',
            'lugares_cercanos': 'Describe los lugares cercanos como centros comerciales, restaurantes, servicios, etc.',
            'latitud': 'Coordenada de latitud para mostrar en el mapa (ej: -38.9516)',
            'longitud': 'Coordenada de longitud para mostrar en el mapa (ej: -68.0591)',
            'amenidades': 'Seleccione las amenidades que incluye la propiedad',
            'ambientes': 'Número total de ambientes (incluye living, comedor, cocina, etc.)',
            'balcon': 'Indica si la propiedad cuenta con balcón',
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
    
    def clean_ambientes(self):
        """Validar el número de ambientes"""
        ambientes = self.cleaned_data.get('ambientes')
        if ambientes is not None:
            if ambientes < 0:
                raise forms.ValidationError('Los ambientes no pueden ser negativos.')
            elif ambientes > 30:
                raise forms.ValidationError('Los ambientes no pueden ser mayor a 30.')
        return ambientes
    
    def clean_imagen_principal(self):
        """Validar la imagen principal"""
        imagen = self.cleaned_data.get('imagen_principal')
        if imagen and hasattr(imagen, 'name') and imagen.name and not imagen.name.startswith('propiedades/'):
            # Solo validar si es un archivo nuevo (no existente)
            # Debug: Log información del archivo
            print(f"DEBUG FORM - Archivo imagen_principal:")
            print(f"  - Nombre: {imagen.name}")
            print(f"  - Tamaño: {imagen.size} bytes")
            print(f"  - Content-Type: {imagen.content_type}")
            
            # Validar tipo de archivo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if imagen.content_type not in allowed_types:
                print(f"DEBUG FORM - Tipo no permitido: {imagen.content_type}")
                raise forms.ValidationError('Solo se permiten archivos de imagen (JPEG, PNG, GIF, WebP).')
            
            # Validar tamaño (20MB máximo)
            if imagen.size > 20 * 1024 * 1024:
                print(f"DEBUG FORM - Tamaño excedido: {imagen.size} bytes")
                raise forms.ValidationError('La imagen debe ser menor a 20MB.')
        return imagen
    
    def clean_imagen_secundaria(self):
        """Validar la imagen secundaria"""
        imagen = self.cleaned_data.get('imagen_secundaria')
        if imagen and hasattr(imagen, 'name') and imagen.name and not imagen.name.startswith('propiedades/'):
            # Solo validar si es un archivo nuevo (no existente)
            # Validar tipo de archivo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if imagen.content_type not in allowed_types:
                raise forms.ValidationError('Solo se permiten archivos de imagen (JPEG, PNG, GIF, WebP).')
            
            # Validar tamaño (20MB máximo)
            if imagen.size > 20 * 1024 * 1024:
                raise forms.ValidationError('La imagen debe ser menor a 20MB.')
        return imagen
    
    def clean_latitud(self):
        """Validar que la latitud esté en el rango correcto"""
        latitud = self.cleaned_data.get('latitud')
        if latitud is not None:  # Solo validar si se proporciona
            if latitud < -90 or latitud > 90:
                raise forms.ValidationError('La latitud debe estar entre -90 y 90 grados.')
        return latitud
    
    def clean_longitud(self):
        """Validar que la longitud esté en el rango correcto"""
        longitud = self.cleaned_data.get('longitud')
        if longitud is not None:  # Solo validar si se proporciona
            if longitud < -180 or longitud > 180:
                raise forms.ValidationError('La longitud debe estar entre -180 y 180 grados.')
        return longitud
    
    def clean_ciudad(self):
        """Validar la ciudad"""
        ciudad = self.cleaned_data.get('ciudad')
        if ciudad and ciudad.strip():  # Solo validar si se proporciona
            ciudad = ciudad.strip()
            if len(ciudad) < 2:
                raise forms.ValidationError('La ciudad debe tener al menos 2 caracteres.')
            elif len(ciudad) > 100:
                raise forms.ValidationError('La ciudad no puede tener más de 100 caracteres.')
            # Validar que solo contenga letras, espacios y guiones (más flexible)
            import re
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-\.]+$', ciudad):
                raise forms.ValidationError('La ciudad solo puede contener letras, espacios, guiones y puntos.')
        return ciudad
    
    def clean_lugares_cercanos(self):
        """Validar los lugares cercanos"""
        lugares = self.cleaned_data.get('lugares_cercanos')
        if lugares and lugares.strip():  # Solo validar si se proporciona
            lugares = lugares.strip()
            if len(lugares) < 10:
                raise forms.ValidationError('Los lugares cercanos deben tener al menos 10 caracteres.')
            elif len(lugares) > 500:
                raise forms.ValidationError('Los lugares cercanos no pueden tener más de 500 caracteres.')
        return lugares
    
    def clean_tipo(self):
        """Validar que el tipo esté seleccionado"""
        tipo = self.cleaned_data.get('tipo')
        if not tipo:
            raise forms.ValidationError('Debe seleccionar un tipo de propiedad.')
        return tipo
    
    def clean_operacion(self):
        """Validar que la operación esté seleccionada"""
        operacion = self.cleaned_data.get('operacion')
        if not operacion:
            raise forms.ValidationError('Debe seleccionar un tipo de operación.')
        return operacion
    
    def clean_estado(self):
        """Validar que el estado esté seleccionado"""
        estado = self.cleaned_data.get('estado')
        if not estado:
            raise forms.ValidationError('Debe seleccionar un estado.')
        return estado
    
    def clean(self):
        """Validaciones cruzadas entre campos"""
        cleaned_data = super().clean()
        latitud = cleaned_data.get('latitud')
        longitud = cleaned_data.get('longitud')
        
        # Validar que las coordenadas estén dentro de Chile (aproximadamente)
        # Solo validar si ambas coordenadas están presentes
        if latitud is not None and longitud is not None:
            # Hacer la validación más flexible para permitir coordenadas de Argentina también
            if latitud < -60 or latitud > -15:
                # Solo mostrar advertencia, no error
                print(f"ADVERTENCIA: Latitud {latitud} puede estar fuera del rango esperado")
            if longitud < -80 or longitud > -60:
                # Solo mostrar advertencia, no error  
                print(f"ADVERTENCIA: Longitud {longitud} puede estar fuera del rango esperado")
        
        return cleaned_data


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
                'class': 'form-control',
                'placeholder': 'Ingrese su nombre completo',
                'required': True,
                'maxlength': '100'
            }),
            'email_usuario': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su email',
                'required': True
            }),
            'telefono_usuario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su teléfono (opcional)',
                'maxlength': '20'
            }),
            'calificacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '5',
                'required': True,
                'id': 'calificacion'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de su reseña',
                'required': True,
                'maxlength': '200'
            }),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escriba su comentario sobre la propiedad',
                'required': True
            }),
        }
        labels = {
            'nombre_usuario': 'Nombre completo',
            'email_usuario': 'Email',
            'telefono_usuario': 'Teléfono',
            'calificacion': 'Calificación (1-5 estrellas)',
            'titulo': 'Título de la reseña',
            'comentario': 'Comentario',
        }
    
    def clean_nombre_usuario(self):
        """Validar el nombre del usuario"""
        nombre = self.cleaned_data.get('nombre_usuario')
        if nombre:
            if len(nombre.strip()) < 2:
                raise forms.ValidationError('El nombre debe tener al menos 2 caracteres.')
            elif len(nombre) > 100:
                raise forms.ValidationError('El nombre no puede tener más de 100 caracteres.')
        return nombre.strip()
    
    def clean_email_usuario(self):
        """Validar el email del usuario"""
        email = self.cleaned_data.get('email_usuario')
        if email:
            if len(email) > 254:  # Límite estándar de email
                raise forms.ValidationError('El email no puede tener más de 254 caracteres.')
        return email
    
    def clean_telefono_usuario(self):
        """Validar el teléfono del usuario"""
        telefono = self.cleaned_data.get('telefono_usuario')
        if telefono:
            # Remover espacios y caracteres especiales para validar
            telefono_limpio = ''.join(filter(str.isdigit, telefono))
            if len(telefono_limpio) < 7:
                raise forms.ValidationError('El teléfono debe tener al menos 7 dígitos.')
            elif len(telefono) > 20:
                raise forms.ValidationError('El teléfono no puede tener más de 20 caracteres.')
        return telefono
    
    def clean_calificacion(self):
        """Validar la calificación"""
        calificacion = self.cleaned_data.get('calificacion')
        if calificacion:
            if calificacion < 1 or calificacion > 5:
                raise forms.ValidationError('La calificación debe estar entre 1 y 5 estrellas.')
        return calificacion
    
    def clean_titulo(self):
        """Validar el título de la reseña"""
        titulo = self.cleaned_data.get('titulo')
        if titulo:
            if len(titulo.strip()) < 5:
                raise forms.ValidationError('El título debe tener al menos 5 caracteres.')
            elif len(titulo) > 200:
                raise forms.ValidationError('El título no puede tener más de 200 caracteres.')
        return titulo.strip()
    
    def clean_comentario(self):
        """Validar el comentario"""
        comentario = self.cleaned_data.get('comentario')
        if comentario:
            if len(comentario.strip()) < 10:
                raise forms.ValidationError('El comentario debe tener al menos 10 caracteres.')
            elif len(comentario) > 2000:
                raise forms.ValidationError('El comentario no puede tener más de 2000 caracteres.')
        return comentario.strip()
