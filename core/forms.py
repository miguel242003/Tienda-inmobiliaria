from django import forms
from django.core.exceptions import ValidationError
from .models import CVSubmission, ContactSubmission


class CVSubmissionForm(forms.ModelForm):
    """Formulario para envío de CV"""
    
    class Meta:
        model = CVSubmission
        fields = [
            'nombre_completo', 
            'email', 
            'telefono', 
            'posicion_interes', 
            'anos_experiencia', 
            'nivel_educativo', 
            'cv_file', 
            'carta_presentacion'
        ]
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre completo',
                'required': True,
                'minlength': '2',
                'maxlength': '200',
                'pattern': '[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\\s\\-\\\'\\.]+',
                'title': 'Solo se permiten letras, espacios, guiones, apostrofes y puntos'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com',
                'required': True,
                'maxlength': '254',
                'title': 'Ingresa un correo electrónico válido'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+5491123456789',
                'required': True,
                'pattern': '^\\+?[0-9\\s\\-\\(\\)]{8,15}$',
                'title': 'Formato: +5491123456789 o 5491123456789 (8-15 dígitos)',
                'minlength': '8',
                'maxlength': '15'
            }),
            'posicion_interes': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
                'title': 'Selecciona una posición de interés'
            }),
            'anos_experiencia': forms.Select(attrs={
                'class': 'form-select',
                'title': 'Selecciona tu experiencia (opcional)'
            }),
            'nivel_educativo': forms.Select(attrs={
                'class': 'form-select',
                'title': 'Selecciona tu nivel educativo (opcional)'
            }),
            'cv_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
                'required': True,
                'title': 'Solo archivos PDF, DOC o DOCX (máximo 5MB)'
            }),
            'carta_presentacion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Cuéntanos por qué te interesa trabajar con nosotros...',
                'maxlength': '2000',
                'title': 'Máximo 2000 caracteres'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Agregar opciones vacías para los campos opcionales
        self.fields['anos_experiencia'].choices = [('', 'Selecciona experiencia')] + list(self.fields['anos_experiencia'].choices)[1:]
        self.fields['nivel_educativo'].choices = [('', 'Selecciona nivel educativo')] + list(self.fields['nivel_educativo'].choices)[1:]
        self.fields['posicion_interes'].choices = [('', 'Selecciona una posición')] + list(self.fields['posicion_interes'].choices)[1:]
        
        # Marcar campos requeridos
        self.fields['nombre_completo'].required = True
        self.fields['email'].required = True
        self.fields['telefono'].required = True
        self.fields['posicion_interes'].required = True
        self.fields['cv_file'].required = True
    
    def clean_cv_file(self):
        """Validación personalizada para el archivo CV"""
        file = self.cleaned_data.get('cv_file')
        
        if file:
            # Validar tamaño del archivo (5MB máximo)
            max_size = 5 * 1024 * 1024  # 5MB
            if file.size > max_size:
                raise ValidationError('El archivo no puede ser mayor a 5MB.')
            
            # Validar tipo de archivo
            allowed_types = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]
            
            if file.content_type not in allowed_types:
                raise ValidationError('Solo se permiten archivos PDF, DOC o DOCX.')
            
            # Validar extensión del archivo
            allowed_extensions = ['.pdf', '.doc', '.docx']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise ValidationError('Solo se permiten archivos PDF, DOC o DOCX.')
        
        return file
    
    def clean_nombre_completo(self):
        """Validación personalizada para el nombre completo"""
        nombre = self.cleaned_data.get('nombre_completo')
        
        if not nombre:
            raise ValidationError('El nombre completo es obligatorio.')
        
        # Validar longitud mínima
        if len(nombre.strip()) < 2:
            raise ValidationError('El nombre debe tener al menos 2 caracteres.')
        
        # Validar longitud máxima
        if len(nombre) > 200:
            raise ValidationError('El nombre no puede exceder los 200 caracteres.')
        
        # Validar que contenga solo letras, espacios y algunos caracteres especiales
        import re
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-\'\.]+$', nombre):
            raise ValidationError('El nombre solo puede contener letras, espacios, guiones, apostrofes y puntos.')
        
        # Validar que no sea solo espacios
        if not nombre.strip():
            raise ValidationError('El nombre no puede estar vacío.')
        
        return nombre.strip()
    
    def clean_email(self):
        """Validación personalizada para el email"""
        from django.utils import timezone
        from datetime import timedelta
        
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError('El correo electrónico es obligatorio.')
        
        # Validar formato de email
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValidationError('Por favor ingresa un correo electrónico válido.')
        
        # Validar longitud máxima
        if len(email) > 254:
            raise ValidationError('El correo electrónico no puede exceder los 254 caracteres.')
        
        # Normalizar email (convertir a minúsculas)
        email_normalizado = email.lower().strip()
        
        # 🔒 VALIDACIÓN: Solo permitir un CV cada 20 días por email
        tiempo_limite = timezone.now() - timedelta(days=20)
        
        ultimo_cv = CVSubmission.objects.filter(
            email=email_normalizado,
            fecha_envio__gte=tiempo_limite
        ).first()
        
        if ultimo_cv:
            tiempo_transcurrido = timezone.now() - ultimo_cv.fecha_envio
            dias_transcurridos = int(tiempo_transcurrido.total_seconds() / 86400)  # 86400 segundos = 1 día
            dias_restantes = 20 - dias_transcurridos
            
            raise ValidationError(
                f'Ya has enviado un CV con este correo electrónico el {ultimo_cv.fecha_envio.strftime("%d/%m/%Y")}. '
                f'Por favor espera {dias_restantes} día(s) más antes de enviar otro CV.'
            )
        
        return email_normalizado
    
    def clean_telefono(self):
        """Validación personalizada para el teléfono"""
        telefono = self.cleaned_data.get('telefono')
        
        if not telefono:
            raise ValidationError('El teléfono es obligatorio.')
        
        # Limpiar el teléfono de espacios y caracteres especiales
        import re
        telefono_limpio = re.sub(r'[^\d+]', '', telefono)
        
        # Validar longitud mínima
        if len(telefono_limpio) < 8:
            raise ValidationError('El teléfono debe tener al menos 8 dígitos.')
        
        # Validar longitud máxima
        if len(telefono_limpio) > 15:
            raise ValidationError('El teléfono no puede exceder los 15 dígitos.')
        
        # Validar que contenga solo números y opcionalmente un + al inicio
        if not re.match(r'^\+?[0-9]+$', telefono_limpio):
            raise ValidationError('El teléfono solo puede contener números y opcionalmente un + al inicio.')
        
        return telefono_limpio
    
    def clean_posicion_interes(self):
        """Validación personalizada para la posición de interés"""
        posicion = self.cleaned_data.get('posicion_interes')
        
        if not posicion:
            raise ValidationError('Debes seleccionar una posición de interés.')
        
        # Validar que la posición esté en las opciones válidas
        valid_positions = [choice[0] for choice in CVSubmission.POSITION_CHOICES]
        if posicion not in valid_positions:
            raise ValidationError('La posición seleccionada no es válida.')
        
        return posicion
    
    def clean_anos_experiencia(self):
        """Validación personalizada para años de experiencia"""
        experiencia = self.cleaned_data.get('anos_experiencia')
        
        if experiencia:  # Solo validar si se proporciona (es opcional)
            valid_experiences = [choice[0] for choice in CVSubmission.EXPERIENCE_CHOICES]
            if experiencia not in valid_experiences:
                raise ValidationError('La experiencia seleccionada no es válida.')
        
        return experiencia
    
    def clean_nivel_educativo(self):
        """Validación personalizada para nivel educativo"""
        nivel = self.cleaned_data.get('nivel_educativo')
        
        if nivel:  # Solo validar si se proporciona (es opcional)
            valid_levels = [choice[0] for choice in CVSubmission.EDUCATION_CHOICES]
            if nivel not in valid_levels:
                raise ValidationError('El nivel educativo seleccionado no es válido.')
        
        return nivel
    
    def clean_carta_presentacion(self):
        """Validación personalizada para la carta de presentación"""
        carta = self.cleaned_data.get('carta_presentacion')
        
        if carta:  # Solo validar si se proporciona (es opcional)
            # Validar longitud máxima
            if len(carta) > 2000:
                raise ValidationError('La carta de presentación no puede exceder los 2000 caracteres.')
            
            # Validar que no sea solo espacios
            if not carta.strip():
                raise ValidationError('La carta de presentación no puede estar vacía.')
            
            return carta.strip()
        
        return carta


class ContactSubmissionForm(forms.ModelForm):
    """Formulario para envío de mensaje de contacto"""
    
    class Meta:
        model = ContactSubmission
        fields = ['nombre', 'email', 'telefono', 'asunto', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre completo',
                'required': True,
                'minlength': '2',
                'maxlength': '200',
                'pattern': '[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\\s\\-\\\'\\.]+',
                'title': 'Solo se permiten letras, espacios, guiones, apostrofes y puntos'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com',
                'required': True,
                'maxlength': '254',
                'title': 'Ingresa un correo electrónico válido'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+5491123456789',
                'required': True,
                'pattern': '^\\+?[0-9\\s\\-\\(\\)]{8,15}$',
                'title': 'Formato: +5491123456789 o 5491123456789 (8-15 dígitos)',
                'minlength': '8',
                'maxlength': '15'
            }),
            'asunto': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
                'title': 'Selecciona un asunto'
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Cuéntanos cómo podemos ayudarte...',
                'required': True,
                'minlength': '10',
                'maxlength': '2000',
                'title': 'Mínimo 10 caracteres, máximo 2000'
            })
        }
    
    def __init__(self, *args, **kwargs):
        # Extraer parámetro personalizado para saber si es consulta de propiedad
        self.es_consulta_propiedad = kwargs.pop('es_consulta_propiedad', False)
        super().__init__(*args, **kwargs)
        
        # Las opciones del asunto ya incluyen la opción vacía en el modelo
        # No necesitamos modificar las choices aquí
        
        # Marcar campos requeridos
        self.fields['nombre'].required = True
        self.fields['email'].required = True
        self.fields['telefono'].required = True
        self.fields['asunto'].required = True
        self.fields['mensaje'].required = True
    
    def clean_nombre(self):
        """Validación personalizada para el nombre"""
        nombre = self.cleaned_data.get('nombre')
        
        if not nombre:
            raise ValidationError('El nombre es obligatorio.')
        
        # Validar longitud mínima
        if len(nombre.strip()) < 2:
            raise ValidationError('El nombre debe tener al menos 2 caracteres.')
        
        # Validar longitud máxima
        if len(nombre) > 200:
            raise ValidationError('El nombre no puede exceder los 200 caracteres.')
        
        # Validar que contenga solo letras, espacios y algunos caracteres especiales
        import re
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-\'\.]+$', nombre):
            raise ValidationError('El nombre solo puede contener letras, espacios, guiones, apostrofes y puntos.')
        
        # Validar que no sea solo espacios
        if not nombre.strip():
            raise ValidationError('El nombre no puede estar vacío.')
        
        return nombre.strip()
    
    def clean_email(self):
        """Validación personalizada para el email"""
        from django.utils import timezone
        from datetime import timedelta
        
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError('El correo electrónico es obligatorio.')
        
        # Validar formato de email
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValidationError('Por favor ingresa un correo electrónico válido.')
        
        # Validar longitud máxima
        if len(email) > 254:
            raise ValidationError('El correo electrónico no puede exceder los 254 caracteres.')
        
        # Normalizar email (convertir a minúsculas)
        email_normalizado = email.lower().strip()
        
        # Validar límite de tiempo entre envíos (15 minutos)
        # Filtrar solo por el tipo de formulario correspondiente
        tiempo_limite = timezone.now() - timedelta(minutes=15)
        
        if self.es_consulta_propiedad:
            # Para consultas de propiedad, buscar solo envíos que contengan información de propiedad
            ultimo_envio = ContactSubmission.objects.filter(
                email=email_normalizado,
                fecha_envio__gte=tiempo_limite,
                mensaje__contains='--- Información de la Propiedad ---'
            ).first()
            tipo_formulario = 'consulta de propiedad'
        else:
            # Para contacto general, buscar solo envíos que NO contengan información de propiedad
            ultimo_envio = ContactSubmission.objects.filter(
                email=email_normalizado,
                fecha_envio__gte=tiempo_limite
            ).exclude(
                mensaje__contains='--- Información de la Propiedad ---'
            ).first()
            tipo_formulario = 'formulario de contacto'
        
        if ultimo_envio:
            tiempo_transcurrido = timezone.now() - ultimo_envio.fecha_envio
            minutos_restantes = 15 - int(tiempo_transcurrido.total_seconds() / 60)
            raise ValidationError(
                f'Ya has enviado un {tipo_formulario} recientemente. '
                f'Por favor espera {minutos_restantes} minuto(s) antes de enviar otro.'
            )
        
        return email_normalizado
    
    def clean_telefono(self):
        """Validación personalizada para el teléfono"""
        telefono = self.cleaned_data.get('telefono')
        
        if not telefono:
            raise ValidationError('El teléfono es obligatorio.')
        
        # Limpiar el teléfono de espacios y caracteres especiales
        import re
        telefono_limpio = re.sub(r'[^\d+]', '', telefono)
        
        # Validar longitud mínima
        if len(telefono_limpio) < 8:
            raise ValidationError('El teléfono debe tener al menos 8 dígitos.')
        
        # Validar longitud máxima
        if len(telefono_limpio) > 15:
            raise ValidationError('El teléfono no puede exceder los 15 dígitos.')
        
        # Validar que contenga solo números y opcionalmente un + al inicio
        if not re.match(r'^\+?[0-9]+$', telefono_limpio):
            raise ValidationError('El teléfono solo puede contener números y opcionalmente un + al inicio.')
        
        return telefono_limpio
    
    def clean_asunto(self):
        """Validación personalizada para el asunto"""
        asunto = self.cleaned_data.get('asunto')
        
        if not asunto:
            raise ValidationError('Debes seleccionar un asunto.')
        
        # Validar que el asunto esté en las opciones válidas
        valid_asuntos = [choice[0] for choice in ContactSubmission.ASUNTO_CHOICES]
        if asunto not in valid_asuntos:
            raise ValidationError('El asunto seleccionado no es válido.')
        
        return asunto
    
    def clean_mensaje(self):
        """Validación personalizada para el mensaje"""
        mensaje = self.cleaned_data.get('mensaje')
        
        if not mensaje:
            raise ValidationError('El mensaje es obligatorio.')
        
        # Validar longitud mínima
        if len(mensaje.strip()) < 10:
            raise ValidationError('El mensaje debe tener al menos 10 caracteres.')
        
        # Validar longitud máxima
        if len(mensaje) > 2000:
            raise ValidationError('El mensaje no puede exceder los 2000 caracteres.')
        
        # Validar que no sea solo espacios
        if not mensaje.strip():
            raise ValidationError('El mensaje no puede estar vacío.')
        
        return mensaje.strip()
    
