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
        fields = ['email', 'password', 'confirmar_password']
        widgets = {
            'password': forms.PasswordInput(),
        }
        help_texts = {
            'email': 'Este será el correo para acceder al panel administrativo',
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
