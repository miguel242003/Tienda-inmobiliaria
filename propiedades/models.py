from django.db import models
from django.core.validators import MinValueValidator

class Propiedad(models.Model):
    TIPO_CHOICES = [
        ('casa', 'Casa'),
        ('apartamento', 'Apartamento'),
        ('terreno', 'Terreno'),
        ('local', 'Local Comercial'),
        ('oficina', 'Oficina'),
    ]
    
    OPERACION_CHOICES = [
        ('venta', 'Venta'),
        ('alquiler', 'Alquiler'),
        ('alquiler_temporal', 'Alquiler Temporal'),
    ]
    
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('vendida', 'Vendida'),
        ('reservada', 'Reservada'),
    ]
    
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descripcion = models.TextField(verbose_name="Descripción")
    precio = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name="Precio"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de Propiedad")
    operacion = models.CharField(max_length=20, choices=OPERACION_CHOICES, default='venta', verbose_name="Tipo de Operación")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible', verbose_name="Estado")
    ubicacion = models.CharField(max_length=300, verbose_name="Ubicación")
    metros_cuadrados = models.PositiveIntegerField(verbose_name="Metros Cuadrados")
    habitaciones = models.PositiveIntegerField(default=0, verbose_name="Habitaciones")
    banos = models.PositiveIntegerField(default=0, verbose_name="Baños")
    imagen_principal = models.ImageField(upload_to='propiedades/', blank=True, null=True, verbose_name="Imagen Principal")
    administrador = models.ForeignKey(
        'login.AdminCredentials',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Administrador que creó la propiedad"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    class Meta:
        verbose_name = "Propiedad"
        verbose_name_plural = "Propiedades"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.titulo
    
    def get_precio_formateado(self):
        return f"${self.precio:,.2f}"
