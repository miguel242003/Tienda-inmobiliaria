from django.contrib import admin
from .models import Propiedad

@admin.register(Propiedad)
class PropiedadAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'precio', 'ubicacion', 'estado', 'metros_cuadrados', 'habitaciones', 'banos', 'fecha_creacion')
    list_filter = ('tipo', 'estado', 'fecha_creacion', 'habitaciones', 'banos')
    search_fields = ('titulo', 'descripcion', 'ubicacion')
    list_editable = ('precio', 'estado')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'tipo', 'estado')
        }),
        ('Precio y Ubicación', {
            'fields': ('precio', 'ubicacion')
        }),
        ('Características', {
            'fields': ('metros_cuadrados', 'habitaciones', 'banos')
        }),
        ('Imagen', {
            'fields': ('imagen_principal',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_precio_formateado(self, obj):
        return obj.get_precio_formateado()
    get_precio_formateado.short_description = 'Precio'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
    
    class Media:
        css = {
            'all': ('admin/css/propiedad_admin.css',)
        }
        js = ('admin/js/propiedad_admin.js',)
