from django import forms

class TwoFactorSetupForm(forms.Form):
    """Formulario para configurar 2FA"""
    totp_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'maxlength': '6',
            'pattern': '[0-9]{6}',
            'inputmode': 'numeric'
        }),
        label="Código de Verificación",
        help_text="Ingresa el código de 6 dígitos de Google Authenticator"
    )
    
    def clean_totp_code(self):
        code = self.cleaned_data.get('totp_code')
        if code and not code.isdigit():
            raise forms.ValidationError("El código debe contener solo números")
        return code

class TwoFactorVerifyForm(forms.Form):
    """Formulario para verificar código 2FA durante el login"""
    totp_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': '000000',
            'maxlength': '6',
            'pattern': '[0-9]{6}',
            'inputmode': 'numeric',
            'autocomplete': 'one-time-code'
        }),
        label="Código de Verificación",
        help_text="Ingresa el código de 6 dígitos de Google Authenticator"
    )
    
    def clean_totp_code(self):
        code = self.cleaned_data.get('totp_code')
        if code and not code.isdigit():
            raise forms.ValidationError("El código debe contener solo números")
        return code

class BackupCodeForm(forms.Form):
    """Formulario para usar códigos de respaldo"""
    backup_code = forms.CharField(
        max_length=8,
        min_length=8,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': 'XXXXXXXX',
            'maxlength': '8',
            'pattern': '[A-Z0-9]{8}',
            'style': 'text-transform: uppercase;'
        }),
        label="Código de Respaldo",
        help_text="Ingresa uno de tus códigos de respaldo de 8 caracteres"
    )
    
    def clean_backup_code(self):
        code = self.cleaned_data.get('backup_code', '').upper()
        if code and not code.isalnum():
            raise forms.ValidationError("El código debe contener solo letras y números")
        return code
