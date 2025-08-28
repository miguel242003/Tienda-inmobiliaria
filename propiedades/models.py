from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.urls import reverse

class Amenidad(models.Model):
    """Modelo para las amenidades de las propiedades"""
    nombre = models.CharField(max_length=100, unique=True)
    icono = models.CharField(max_length=50, help_text="Clase de Font Awesome (ej: fa-swimming-pool)")
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Amenidad"
        verbose_name_plural = "Amenidades"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

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
    imagen_secundaria = models.ImageField(upload_to='propiedades/', blank=True, null=True, verbose_name="Imagen Secundaria")
    administrador = models.ForeignKey(
        'login.AdminCredentials',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Administrador que creó la propiedad"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    # Agregar campo para amenidades
    amenidades = models.ManyToManyField(Amenidad, blank=True, verbose_name="Amenidades incluidas")
    
    class Meta:
        verbose_name = "Propiedad"
        verbose_name_plural = "Propiedades"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.titulo
    
    def get_precio_formateado(self):
        return f"${self.precio:,.2f}"
    
    def get_total_fotos(self):
        """Retorna el total de fotos de la propiedad"""
        return self.fotos.count()
    
    def get_foto_principal(self):
        """Retorna la foto principal o la primera foto disponible"""
        if self.imagen_principal:
            return self.imagen_principal
        elif self.fotos.exists():
            return self.fotos.first().imagen
        return None
    
    def get_foto_secundaria(self):
        """Retorna la foto secundaria o la segunda foto disponible"""
        if self.imagen_secundaria:
            return self.imagen_secundaria
        elif self.fotos.count() >= 2:
            return self.fotos.all()[1].imagen
        return None
    
    def get_capacidad_personas(self):
        """Retorna la capacidad de personas (habitaciones + 2)"""
        return self.habitaciones + 2
    
    def get_foto_por_posicion(self, posicion):
        """Retorna la foto en la posición especificada (1, 2, 3, etc.)"""
        if posicion == 1 and self.fotos.exists():
            return self.fotos.first()
        elif posicion == 2 and self.fotos.count() >= 2:
            return self.fotos.all()[1]
        elif posicion == 3 and self.fotos.count() >= 3:
            return self.fotos.all()[2]
        return None

class FotoPropiedad(models.Model):
    """Modelo para almacenar múltiples fotos de una propiedad"""
    propiedad = models.ForeignKey(
        Propiedad, 
        on_delete=models.CASCADE, 
        related_name='fotos',
        verbose_name="Propiedad"
    )
    imagen = models.ImageField(
        upload_to='propiedades/fotos/', 
        verbose_name="Imagen"
    )
    descripcion = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name="Descripción de la imagen"
    )
    orden = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden de la imagen"
    )
    fecha_subida = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de subida"
    )
    
    class Meta:
        verbose_name = "Foto de Propiedad"
        verbose_name_plural = "Fotos de Propiedades"
        ordering = ['orden', 'fecha_subida']
    
    def __str__(self):
        return f"Foto {self.orden} de {self.propiedad.titulo}"
