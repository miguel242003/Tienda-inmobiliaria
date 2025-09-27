from django import forms
from django.core.exceptions import ValidationError
from .models import AdminCredentials, PasswordResetCode


class PasswordResetRequestForm(forms.Form):
    """Formulario para solicitar recuperación de contraseña"""
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ingresa tu correo electrónico',
            'autocomplete': 'email'
        }),
        label="Correo Electrónico",
        help_text="Ingresa el correo electrónico asociado a tu cuenta de administrador"
    )
    
    def clean_email(self):
        email = self.cleaned_data['email']
        
        # Verificar que el email existe en AdminCredentials
        if not AdminCredentials.objects.filter(email=email, activo=True).exists():
            raise ValidationError("No existe una cuenta de administrador con este correo electrónico.")
        
        return email


class PasswordResetVerifyForm(forms.Form):
    """Formulario para verificar código y cambiar contraseña"""
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': '000000',
            'maxlength': '6',
            'pattern': '[0-9]{6}',
            'inputmode': 'numeric',
            'autocomplete': 'one-time-code'
        }),
        label="Código de Verificación",
        help_text="Ingresa el código de 6 dígitos que enviamos a tu correo"
    )
    
    new_password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Nueva contraseña',
            'autocomplete': 'new-password'
        }),
        label="Nueva Contraseña",
        help_text="Mínimo 6 caracteres"
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirmar nueva contraseña',
            'autocomplete': 'new-password'
        }),
        label="Confirmar Nueva Contraseña"
    )
    
    def clean_code(self):
        code = self.cleaned_data['code']
        
        if not code.isdigit() or len(code) != 6:
            raise ValidationError("El código debe ser de 6 dígitos numéricos.")
        
        return code
    
    def clean_confirm_password(self):
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError("Las contraseñas no coinciden.")
        
        return confirm_password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data
