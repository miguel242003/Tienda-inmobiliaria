from django.contrib import admin
from .models import AdminCredentials

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
