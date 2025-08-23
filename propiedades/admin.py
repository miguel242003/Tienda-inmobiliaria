from django.contrib import admin
from .models import Propiedad

@admin.register(Propiedad)
class PropiedadAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'operacion', 'precio', 'get_precio_ars', 'ubicacion', 'estado', 'administrador', 'metros_cuadrados', 'habitaciones', 'banos', 'fecha_creacion')
    list_filter = ('tipo', 'operacion', 'estado', 'fecha_creacion', 'habitaciones', 'banos', 'administrador')
    search_fields = ('titulo', 'descripcion', 'ubicacion', 'administrador__nombre', 'administrador__apellido')
    list_editable = ('precio', 'estado', 'operacion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'tipo', 'operacion', 'estado')
        }),
        ('Precio y Ubicación', {
            'fields': ('precio', 'ubicacion'),
            'description': 'El precio debe estar en pesos argentinos (ARS)'
        }),
        ('Características', {
            'fields': ('metros_cuadrados', 'habitaciones', 'banos')
        }),
        ('Imagen', {
            'fields': ('imagen_principal',)
        }),
        ('Administración', {
            'fields': ('administrador',),
            'description': 'Administrador responsable de esta propiedad'
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_precio_ars(self, obj):
        """Mostrar precio en formato argentino"""
        if obj.precio:
            return f"$ {obj.precio:,.0f} ARS"
        return "-"
    get_precio_ars.short_description = 'Precio (ARS)'
    get_precio_ars.admin_order_field = 'precio'
    
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
