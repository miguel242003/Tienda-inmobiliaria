from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import CVSubmission, ContactSubmission


@admin.register(CVSubmission)
class CVSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'nombre_completo', 
        'email', 
        'posicion_interes', 
        'fecha_envio', 
        'procesado',
        'file_info',
        'contact_actions'
    ]
    list_filter = [
        'posicion_interes',
        'anos_experiencia',
        'nivel_educativo',
        'procesado',
        'fecha_envio'
    ]
    search_fields = [
        'nombre_completo',
        'email',
        'telefono',
        'carta_presentacion'
    ]
    readonly_fields = [
        'fecha_envio',
        'file_info',
        'file_size_display'
    ]
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre_completo', 'email', 'telefono')
        }),
        ('Información Profesional', {
            'fields': ('posicion_interes', 'anos_experiencia', 'nivel_educativo')
        }),
        ('Archivos', {
            'fields': ('cv_file', 'file_info', 'file_size_display', 'carta_presentacion')
        }),
        ('Gestión', {
            'fields': ('procesado', 'notas_admin', 'fecha_envio'),
            'classes': ('collapse',)
        })
    )
    ordering = ['-fecha_envio']
    date_hierarchy = 'fecha_envio'
    actions = ['mark_as_processed', 'mark_as_unprocessed']
    
    def file_info(self, obj):
        """Muestra información del archivo CV"""
        if obj.cv_file:
            return format_html(
                '<strong>{}</strong><br>'
                '<small>Tamaño: {} | Formato: {}</small>',
                obj.cv_file.name.split('/')[-1],
                obj.get_file_size(),
                obj.get_file_extension()
            )
        return "Sin archivo"
    file_info.short_description = "Archivo CV"
    
    def file_size_display(self, obj):
        """Muestra el tamaño del archivo"""
        return obj.get_file_size()
    file_size_display.short_description = "Tamaño del Archivo"
    
    def contact_actions(self, obj):
        """Botones de acción rápida"""
        email_url = f"mailto:{obj.email}"
        return format_html(
            '<a href="{}" class="button" title="Enviar email">📧</a>',
            email_url
        )
    contact_actions.short_description = "Acciones"
    
    def mark_as_processed(self, request, queryset):
        """Marca los CVs seleccionados como procesados"""
        updated = queryset.update(procesado=True)
        self.message_user(
            request,
            f'{updated} CV(s) marcado(s) como procesado(s).'
        )
    mark_as_processed.short_description = "Marcar como procesado"
    
    def mark_as_unprocessed(self, request, queryset):
        """Marca los CVs seleccionados como no procesados"""
        updated = queryset.update(procesado=False)
        self.message_user(
            request,
            f'{updated} CV(s) marcado(s) como no procesado(s).'
        )
    mark_as_unprocessed.short_description = "Marcar como no procesado"
    
    def get_queryset(self, request):
        """Optimiza las consultas"""
        return super().get_queryset(request).select_related()
    
    class Media:
        css = {
            'all': ('admin/css/cv_admin.css',)
        }


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 
        'email', 
        'asunto', 
        'fecha_entrada',
        'fecha_salida',
        'fecha_envio', 
        'contact_actions'
    ]
    list_filter = [
        'asunto',
        'fecha_entrada',
        'fecha_salida',
        'fecha_envio'
    ]
    search_fields = [
        'nombre',
        'email',
        'telefono',
        'mensaje'
    ]
    readonly_fields = [
        'fecha_envio'
    ]
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('nombre', 'email', 'telefono')
        }),
        ('Consulta', {
            'fields': ('asunto', 'mensaje')
        }),
        ('Fechas de Estancia', {
            'fields': ('fecha_entrada', 'fecha_salida')
        }),
        ('Metadatos', {
            'fields': ('fecha_envio',),
            'classes': ('collapse',)
        })
    )
    ordering = ['-fecha_envio']
    date_hierarchy = 'fecha_envio'
    
    def contact_actions(self, obj):
        """Botones de acción rápida"""
        email_url = f"mailto:{obj.email}"
        return format_html(
            '<a href="{}" class="button" title="Enviar email">📧</a>',
            email_url
        )
    contact_actions.short_description = "Acciones"
    
    def get_queryset(self, request):
        """Optimiza las consultas"""
        return super().get_queryset(request).select_related()
