from django import forms
from .models import AdminCredentials

class AdminCredentialsForm(forms.ModelForm):
    """Formulario para configurar credenciales del administrador"""
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(),
        label="Confirmar Contraseña",
        help_text="Escribe la misma contraseña para confirmar"
    )
    
    class Meta:
        model = AdminCredentials
        fields = ['nombre', 'apellido', 'email', 'telefono', 'fecha_nacimiento', 'foto_perfil', 'password', 'confirmar_password']
        exclude = ['user']  # Excluir el campo user ya que se asignará después
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa tu nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa tu apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+52-1-33-12345678'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'foto_perfil': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'foto_perfil_input'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mínimo 8 caracteres'
            }),
        }
        help_texts = {
            'nombre': 'Tu nombre completo para mostrar en las propiedades',
            'apellido': 'Tu apellido completo para mostrar en las propiedades',
            'email': 'Este será el correo para acceder al panel administrativo',
            'telefono': 'Tu número de teléfono para que los clientes te contacten',
            'foto_perfil': 'Tu foto de perfil para mostrar en las propiedades (opcional)',
            'password': 'Elige una contraseña segura (mínimo 8 caracteres)',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar_password = cleaned_data.get('confirmar_password')
        
        if password and confirmar_password:
            if password != confirmar_password:
                raise forms.ValidationError("Las contraseñas no coinciden")
            
            if len(password) < 8:
                raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # La contraseña se encripta automáticamente en el modelo
        if commit:
            instance.save()
        return instance

class NuevoUsuarioAdminForm(forms.ModelForm):
    """Formulario para crear un nuevo usuario administrativo"""
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(),
        label="Confirmar Contraseña",
        help_text="Escribe la misma contraseña para confirmar"
    )
    
    class Meta:
        model = AdminCredentials
        fields = ['nombre', 'apellido', 'email', 'telefono', 'fecha_nacimiento', 'foto_perfil', 'password', 'confirmar_password']
        exclude = ['user']  # Excluir el campo user ya que se asignará después
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa el nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa el apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'usuario@email.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+52-1-33-12345678'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'foto_perfil': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'foto_perfil_nuevo_input'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mínimo 8 caracteres'
            }),
        }
        help_texts = {
            'nombre': 'Nombre del nuevo administrador',
            'apellido': 'Apellido del nuevo administrador',
            'email': 'Correo electrónico para acceder al sistema',
            'telefono': 'Número de teléfono de contacto',
            'fecha_nacimiento': 'Fecha de nacimiento (opcional)',
            'foto_perfil': 'Foto de perfil (opcional)',
            'password': 'Contraseña segura (mínimo 8 caracteres)',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar_password = cleaned_data.get('confirmar_password')
        email = cleaned_data.get('email')
        
        if password and confirmar_password:
            if password != confirmar_password:
                raise forms.ValidationError("Las contraseñas no coinciden")
            
            if len(password) < 8:
                raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres")
        
        # Verificar que el email no esté en uso
        if email:
            if AdminCredentials.objects.filter(email=email, activo=True).exists():
                raise forms.ValidationError("Ya existe un usuario administrativo con este correo electrónico")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # La contraseña se encripta automáticamente en el modelo
        if commit:
            instance.save()
        return instance
