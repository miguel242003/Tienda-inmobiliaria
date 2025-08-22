from django.contrib import admin
from .models import AdminCredentials

@admin.register(AdminCredentials)
class AdminCredentialsAdmin(admin.ModelAdmin):
    list_display = ['email', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['email']
    readonly_fields = ['fecha_creacion']
    
    fieldsets = (
        ('Información de Acceso', {
            'fields': ('email', 'password', 'activo')
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Si es una edición
            return self.readonly_fields + ('password',)
        return self.readonly_fields
