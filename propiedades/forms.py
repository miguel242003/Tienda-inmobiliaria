from django import forms
from .models import Propiedad, Amenidad, Resena

class PropiedadForm(forms.ModelForm):
    """Formulario para crear y editar propiedades"""
    
    # Sobrescribir el campo precio para evitar formato automático de decimales
    precio = forms.CharField(
        label='Precio',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 100.000 o 1.500.000',
            'title': 'Ingrese el precio (puede usar punto o coma como separador de miles)',
            'required': True
        })
    )
    
    class Meta:
        model = Propiedad
        fields = [
            'titulo', 'descripcion', 'precio', 'tipo', 'operacion', 'estado',
            'ubicacion', 'ciudad', 'lugares_cercanos', 'metros_cuadrados', 'habitaciones', 'banos',
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
                'step': 'any',
                'min': '-90',
                'max': '90',
                'placeholder': 'Ej: -33.6914783645518',
                'title': 'La latitud debe estar entre -90 y 90 grados',
                'required': True
            }),
            'longitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'min': '-180',
                'max': '180',
                'placeholder': 'Ej: -65.45524318970048',
                'title': 'La longitud debe estar entre -180 y 180 grados',
                'required': True
            }),
        }
        labels = {
            'titulo': 'Título de la Propiedad',
            'descripcion': 'Descripción',
            'tipo': 'Tipo de Propiedad',
            'operacion': 'Tipo de Operación',
            'estado': 'Estado',
            'ubicacion': 'Ubicación',
            'ciudad': 'Ciudad',
            'lugares_cercanos': 'Lugares Cercanos',
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
            'ciudad': 'Ciudad donde se encuentra la propiedad',
            'lugares_cercanos': 'Describe los lugares cercanos como centros comerciales, restaurantes, servicios, etc.',
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
        precio_str = self.cleaned_data.get('precio')
        
        if not precio_str:
            raise forms.ValidationError('El precio es obligatorio.')
        
        # Convertir a string si es necesario
        precio_str = str(precio_str).strip()
        
        # Remover espacios en blanco
        precio_str = precio_str.replace(' ', '')
        
        # Detectar si usa coma como separador decimal o punto
        # Formato argentino: 100.000 o 100.000,50 (punto como separador de miles, coma como decimal)
        # Formato internacional: 100,000 o 100,000.50 (coma como separador de miles, punto como decimal)
        
        # Si tiene tanto punto como coma, determinar cuál es el decimal
        if ',' in precio_str and '.' in precio_str:
            # El último separador es el decimal
            pos_coma = precio_str.rfind(',')
            pos_punto = precio_str.rfind('.')
            
            if pos_punto > pos_coma:
                # Formato internacional: 1.000.000,50 o 1,000,000.50
                # El punto es el decimal, remover comas
                precio_str = precio_str.replace(',', '')
            else:
                # Formato argentino: 1,000,000.50 o 1.000.000,50
                # La coma es el decimal, remover puntos y cambiar coma por punto
                precio_str = precio_str.replace('.', '').replace(',', '.')
        elif ',' in precio_str:
            # Solo tiene coma, puede ser separador de miles o decimal
            partes = precio_str.split(',')
            if len(partes) == 2 and len(partes[1]) <= 2:
                # Es decimal (ej: 100,50)
                precio_str = precio_str.replace(',', '.')
            else:
                # Es separador de miles (ej: 100,000 o 1,000,000)
                precio_str = precio_str.replace(',', '')
        elif '.' in precio_str:
            # Solo tiene punto, puede ser separador de miles o decimal
            partes = precio_str.split('.')
            if len(partes) == 2 and len(partes[1]) <= 2:
                # Es decimal (ej: 100.50)
                # Ya está en formato correcto
                pass
            else:
                # Es separador de miles (ej: 100.000 o 1.000.000)
                precio_str = precio_str.replace('.', '')
        
        # Intentar convertir a decimal
        try:
            from decimal import Decimal, InvalidOperation
            precio = Decimal(precio_str)
        except (ValueError, InvalidOperation):
            raise forms.ValidationError('El precio debe ser un número válido. Ejemplos: 100000, 100.000, 100000.50')
        
        # Validar que sea mayor a 0
        if precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0.')
        
        # Validar que no sea mayor a 999,999,999
        if precio > 999999999:
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
        if latitud is None:
            raise forms.ValidationError('La latitud es obligatoria.')
        if latitud < -90 or latitud > 90:
            raise forms.ValidationError('La latitud debe estar entre -90 y 90 grados.')
        return latitud
    
    def clean_longitud(self):
        """Validar que la longitud esté en el rango correcto"""
        longitud = self.cleaned_data.get('longitud')
        if longitud is None:
            raise forms.ValidationError('La longitud es obligatoria.')
        if longitud < -180 or longitud > 180:
            raise forms.ValidationError('La longitud debe estar entre -180 y 180 grados.')
        return longitud
    
    def clean_ciudad(self):
        """Validar la ciudad"""
        ciudad = self.cleaned_data.get('ciudad')
        if not ciudad or not ciudad.strip():
            raise forms.ValidationError('La ciudad es obligatoria.')
        
        ciudad = ciudad.strip()
        if len(ciudad) < 2:
            raise forms.ValidationError('La ciudad debe tener al menos 2 caracteres.')
        elif len(ciudad) > 100:
            raise forms.ValidationError('La ciudad no puede tener más de 100 caracteres.')
        # Validar que solo contenga letras, espacios y guiones
        import re
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]+$', ciudad):
            raise forms.ValidationError('La ciudad solo puede contener letras, espacios y guiones.')
        return ciudad
    
    def clean_lugares_cercanos(self):
        """Validar los lugares cercanos"""
        lugares = self.cleaned_data.get('lugares_cercanos')
        if not lugares or not lugares.strip():
            raise forms.ValidationError('Los lugares cercanos son obligatorios.')
        
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
        if latitud is not None and longitud is not None:
            if latitud < -56 or latitud > -17:
                raise forms.ValidationError({
                    'latitud': 'La latitud parece estar fuera de Chile. Verifique las coordenadas.'
                })
            if longitud < -76 or longitud > -66:
                raise forms.ValidationError({
                    'longitud': 'La longitud parece estar fuera de Chile. Verifique las coordenadas.'
                })
        
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
