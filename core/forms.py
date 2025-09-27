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
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com',
                'required': True
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 234 567 890'
            }),
            'posicion_interes': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'anos_experiencia': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nivel_educativo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cv_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
                'required': True
            }),
            'carta_presentacion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Cuéntanos por qué te interesa trabajar con nosotros...'
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
    
    def clean_email(self):
        """Validación personalizada para el email"""
        email = self.cleaned_data.get('email')
        
        # Por ahora permitimos múltiples CVs con el mismo email
        # La validación de duplicados se puede reactivar más tarde si es necesario
        
        return email
    
    def clean_telefono(self):
        """Validación personalizada para el teléfono"""
        telefono = self.cleaned_data.get('telefono')
        
        if telefono:
            # Limpiar el teléfono (remover espacios, guiones, paréntesis)
            import re
            cleaned_phone = re.sub(r'[\s\-\(\)]', '', telefono)
            
            # Verificar que solo contenga números y el símbolo +
            if not re.match(r'^\+?[0-9]+$', cleaned_phone):
                raise ValidationError('Por favor ingresa un número de teléfono válido.')
            
            # Verificar longitud mínima
            if len(cleaned_phone) < 10:
                raise ValidationError('El número de teléfono debe tener al menos 10 dígitos.')
        
        return telefono
    
    def clean(self):
        """Validación cruzada de fechas"""
        cleaned_data = super().clean()
        fecha_entrada = cleaned_data.get('fecha_entrada')
        fecha_salida = cleaned_data.get('fecha_salida')
        
        # Validar que la fecha de salida sea posterior a la de entrada
        if fecha_entrada and fecha_salida:
            if fecha_salida <= fecha_entrada:
                raise ValidationError('La fecha de salida debe ser posterior a la fecha de entrada.')
        
        # Validar que las fechas no sean en el pasado
        from django.utils import timezone
        today = timezone.now().date()
        
        if fecha_entrada and fecha_entrada < today:
            raise ValidationError('La fecha de entrada no puede ser en el pasado.')
        
        if fecha_salida and fecha_salida < today:
            raise ValidationError('La fecha de salida no puede ser en el pasado.')
        
        return cleaned_data


class ContactSubmissionForm(forms.ModelForm):
    """Formulario para envío de mensaje de contacto"""
    
    class Meta:
        model = ContactSubmission
        fields = ['nombre', 'email', 'telefono', 'asunto', 'mensaje', 'fecha_entrada', 'fecha_salida']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre completo',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com',
                'required': True
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 234 567 890'
            }),
            'asunto': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Cuéntanos cómo podemos ayudarte...',
                'required': True
            }),
            'fecha_entrada': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Fecha de entrada'
            }),
            'fecha_salida': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Fecha de salida'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # No agregar opción vacía para el asunto, solo mostrar "Alquiler"
        # self.fields['asunto'].choices = [('', 'Selecciona un asunto')] + list(self.fields['asunto'].choices)[1:]
        
        # Marcar campos requeridos
        self.fields['nombre'].required = True
        self.fields['email'].required = True
        self.fields['asunto'].required = True
        self.fields['mensaje'].required = True
    
    def clean_telefono(self):
        """Validación personalizada para el teléfono"""
        telefono = self.cleaned_data.get('telefono')
        
        if telefono:
            # Limpiar el teléfono (remover espacios, guiones, paréntesis)
            import re
            cleaned_phone = re.sub(r'[\s\-\(\)]', '', telefono)
            
            # Verificar que solo contenga números y el símbolo +
            if not re.match(r'^\+?[0-9]+$', cleaned_phone):
                raise ValidationError('Por favor ingresa un número de teléfono válido.')
            
            # Verificar longitud mínima
            if len(cleaned_phone) < 10:
                raise ValidationError('El número de teléfono debe tener al menos 10 dígitos.')
        
        return telefono
    
    def clean(self):
        """Validación cruzada de fechas"""
        cleaned_data = super().clean()
        fecha_entrada = cleaned_data.get('fecha_entrada')
        fecha_salida = cleaned_data.get('fecha_salida')
        
        # Validar que la fecha de salida sea posterior a la de entrada
        if fecha_entrada and fecha_salida:
            if fecha_salida <= fecha_entrada:
                raise ValidationError('La fecha de salida debe ser posterior a la fecha de entrada.')
        
        # Validar que las fechas no sean en el pasado
        from django.utils import timezone
        today = timezone.now().date()
        
        if fecha_entrada and fecha_entrada < today:
            raise ValidationError('La fecha de entrada no puede ser en el pasado.')
        
        if fecha_salida and fecha_salida < today:
            raise ValidationError('La fecha de salida no puede ser en el pasado.')
        
        return cleaned_data
