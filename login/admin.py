from django.contrib import admin
from .models import AdminCredentials, PasswordResetCode

@admin.register(AdminCredentials)
class AdminCredentialsAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'email', 'telefono', 'foto_perfil', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'apellido', 'email', 'telefono']
    readonly_fields = ['fecha_creacion']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'email', 'telefono', 'foto_perfil')
        }),
        ('Información de Acceso', {
            'fields': ('password', 'activo')
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Si es una edición
            return list(self.readonly_fields) + ['password']
        return self.readonly_fields


@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'used', 'created_at', 'expires_at', 'is_valid')
    list_filter = ('used', 'created_at', 'expires_at')
    search_fields = ('email', 'code')
    readonly_fields = ('created_at', 'expires_at', 'is_valid')
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información del Código', {
            'fields': ('email', 'code', 'used')
        }),
        ('Fechas', {
            'fields': ('created_at', 'expires_at', 'is_valid'),
            'classes': ('collapse',)
        }),
    )
    
    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Válido'
    
    def has_add_permission(self, request):
        # No permitir agregar códigos manualmente
        return False
    
    def has_change_permission(self, request, obj=None):
        # Solo permitir marcar como usado
        return False
