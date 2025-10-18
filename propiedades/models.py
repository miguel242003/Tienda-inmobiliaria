from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from core.fields import WebPImageFieldMixin, WebPImageField

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

class Propiedad(WebPImageFieldMixin, models.Model):
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
    slug = models.SlugField(max_length=250, unique=True, blank=True, verbose_name="URL amigable")
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
    ciudad = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ciudad")
    lugares_cercanos = models.TextField(blank=True, null=True, verbose_name="Lugares Cercanos", 
                                       help_text="Describe los lugares cercanos como centros comerciales, restaurantes, servicios, etc.")
    metros_cuadrados = models.PositiveIntegerField(verbose_name="Metros Cuadrados")
    habitaciones = models.PositiveIntegerField(default=0, verbose_name="Habitaciones")
    banos = models.PositiveIntegerField(default=0, verbose_name="Baños")
    ambientes = models.PositiveIntegerField(default=0, verbose_name="Ambientes", 
                                          help_text="Número total de ambientes (incluye living, comedor, cocina, etc.)")
    balcon = models.BooleanField(default=False, verbose_name="Tiene Balcón", 
                                help_text="Indica si la propiedad cuenta con balcón")
    imagen_principal = WebPImageField(upload_to='propiedades/', blank=True, null=True, verbose_name="Imagen Principal", auto_optimize=False)
    imagen_secundaria = WebPImageField(upload_to='propiedades/', blank=True, null=True, verbose_name="Imagen Secundaria", auto_optimize=False)
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
    
    # Campos de coordenadas geográficas
    latitud = models.DecimalField(
        max_digits=20, 
        decimal_places=15, 
        blank=True, 
        null=True, 
        help_text='Coordenada de latitud (ej: -33.6914783645518)',
        verbose_name='Latitud'
    )
    longitud = models.DecimalField(
        max_digits=20, 
        decimal_places=15, 
        blank=True, 
        null=True, 
        help_text='Coordenada de longitud (ej: -65.45524318970048)',
        verbose_name='Longitud'
    )
    
    class Meta:
        verbose_name = "Propiedad"
        verbose_name_plural = "Propiedades"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.titulo
    
    def save(self, *args, **kwargs):
        """Generar slug automáticamente si no existe"""
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.titulo)
            self.slug = base_slug
            
            # Si el slug ya existe, agregar un número al final
            counter = 1
            while Propiedad.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_precio_formateado(self):
        # 🔥 FORMATO ARGENTINO: 110.000 en lugar de 110,000.00
        try:
            # Formatear con punto como separador de miles
            formatted = f"{self.precio:,.0f}".replace(',', '.')
            return f"${formatted}"
        except (ValueError, TypeError):
            return f"${self.precio}"
    
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
    
    
    def get_foto_por_posicion(self, posicion):
        """Retorna la foto en la posición especificada (1, 2, 3, etc.)"""
        if posicion == 1 and self.fotos.exists():
            return self.fotos.first()
        elif posicion == 2 and self.fotos.count() >= 2:
            return self.fotos.all()[1]
        elif posicion == 3 and self.fotos.count() >= 3:
            return self.fotos.all()[2]
        return None
    
    def get_total_clicks(self):
        """Retorna el total de clics en esta propiedad"""
        return self.clicks.count()
    
    def get_clicks_este_mes(self):
        """Retorna los clics de este mes"""
        from django.utils import timezone
        from datetime import datetime
        
        now = timezone.now()
        inicio_mes = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return self.clicks.filter(fecha_click__gte=inicio_mes).count()
    
    def get_clicks_por_mes(self, meses=12):
        """Retorna los clics por mes para los últimos N meses"""
        from django.utils import timezone
        from datetime import datetime, timedelta
        from django.db.models import Count
        from django.db.models.functions import TruncMonth
        
        now = timezone.now()
        inicio_periodo = now - timedelta(days=meses * 30)
        
        clicks_por_mes = self.clicks.filter(
            fecha_click__gte=inicio_periodo
        ).annotate(
            mes=TruncMonth('fecha_click')
        ).values('mes').annotate(
            total=Count('id')
        ).order_by('mes')
        
        # Crear un diccionario con todos los meses
        resultado = {}
        for i in range(meses):
            fecha = now - timedelta(days=i * 30)
            mes_key = fecha.strftime('%Y-%m')
            resultado[mes_key] = 0
        
        # Llenar con datos reales
        for click in clicks_por_mes:
            mes_key = click['mes'].strftime('%Y-%m')
            if mes_key in resultado:
                resultado[mes_key] = click['total']
        
        return resultado

class FotoPropiedad(WebPImageFieldMixin, models.Model):
    """Modelo para almacenar múltiples fotos y videos de una propiedad"""
    
    TIPO_MEDIO_CHOICES = [
        ('imagen', 'Imagen'),
        ('video', 'Video'),
    ]
    
    propiedad = models.ForeignKey(
        Propiedad, 
        on_delete=models.CASCADE, 
        related_name='fotos',
        verbose_name="Propiedad"
    )
    tipo_medio = models.CharField(
        max_length=10,
        choices=TIPO_MEDIO_CHOICES,
        default='imagen',
        verbose_name="Tipo de Medio"
    )
    imagen = WebPImageField(
        upload_to='propiedades/fotos/', 
        verbose_name="Imagen",
        blank=True,
        null=True,
        auto_optimize=False
    )
    video = models.FileField(
        upload_to='propiedades/videos/',
        verbose_name="Video",
        blank=True,
        null=True,
        help_text="Formato de video (MP4, AVI, MOV)"
    )
    descripcion = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name="Descripción del archivo"
    )
    orden = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden del archivo"
    )
    fecha_subida = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de subida"
    )
    
    class Meta:
        verbose_name = "Foto/Video de Propiedad"
        verbose_name_plural = "Fotos/Videos de Propiedades"
        ordering = ['orden', 'fecha_subida']
    
    def __str__(self):
        tipo = "Foto" if self.tipo_medio == 'imagen' else "Video"
        return f"{tipo} {self.orden} de {self.propiedad.titulo}"
    
    def get_archivo_url(self):
        """Retorna la URL del archivo (imagen o video)"""
        if self.tipo_medio == 'imagen' and self.imagen:
            return self.imagen.url
        elif self.tipo_medio == 'video' and self.video:
            return self.video.url
        return None

class ClickPropiedad(models.Model):
    """Modelo para rastrear clics en botones 'Ver Detalle' de propiedades"""
    propiedad = models.ForeignKey(
        Propiedad,
        on_delete=models.CASCADE,
        related_name='clicks',
        verbose_name="Propiedad"
    )
    fecha_click = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha del Click"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP"
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name="User Agent"
    )
    pagina_origen = models.CharField(
        max_length=100,
        choices=[
            ('home', 'Página de Inicio'),
            ('buscar', 'Página de Búsqueda'),
            ('detalle', 'Página de Detalle'),
            ('otra', 'Otra Página'),
        ],
        default='home',
        verbose_name="Página de Origen"
    )
    
    class Meta:
        verbose_name = "Click en Propiedad"
        verbose_name_plural = "Clicks en Propiedades"
        ordering = ['-fecha_click']
    
    def __str__(self):
        return f"Click en {self.propiedad.titulo} - {self.fecha_click.strftime('%d/%m/%Y %H:%M')}"

class Resena(models.Model):
    """Modelo para las reseñas de propiedades"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de Aprobación'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]
    
    propiedad = models.ForeignKey(
        Propiedad,
        on_delete=models.CASCADE,
        related_name='resenas',
        verbose_name="Propiedad"
    )
    nombre_usuario = models.CharField(
        max_length=100,
        verbose_name="Nombre del Usuario"
    )
    email_usuario = models.EmailField(
        verbose_name="Email del Usuario"
    )
    telefono_usuario = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono del Usuario"
    )
    calificacion = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Calificación (1-5 estrellas)"
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título de la Reseña"
    )
    comentario = models.TextField(
        verbose_name="Comentario"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name="Estado de la Reseña"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_moderacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Moderación"
    )
    moderado_por = models.ForeignKey(
        'login.AdminCredentials',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Moderado por"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP"
    )
    
    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Reseña de {self.nombre_usuario} para {self.propiedad.titulo}"
    
    def get_estrellas_html(self):
        """Retorna HTML para mostrar las estrellas de calificación"""
        estrellas_llenas = '★' * self.calificacion
        estrellas_vacias = '☆' * (5 - self.calificacion)
        return f"{estrellas_llenas}{estrellas_vacias}"
    
    def get_estado_badge_class(self):
        """Retorna la clase CSS para el badge del estado"""
        clases = {
            'pendiente': 'bg-yellow-100 text-yellow-800',
            'aprobada': 'bg-green-100 text-green-800',
            'rechazada': 'bg-red-100 text-red-800',
        }
        return clases.get(self.estado, 'bg-gray-100 text-gray-800')
    
    def get_estado_display_color(self):
        """Retorna el color para mostrar el estado"""
        colores = {
            'pendiente': 'yellow',
            'aprobada': 'green',
            'rechazada': 'red',
        }
        return colores.get(self.estado, 'gray')
    
    def aprobar(self, moderador):
        """Aprobar la reseña"""
        from django.utils import timezone
        self.estado = 'aprobada'
        self.moderado_por = moderador
        self.fecha_moderacion = timezone.now()
        self.save()
    
    def rechazar(self, moderador):
        """Rechazar la reseña"""
        from django.utils import timezone
        self.estado = 'rechazada'
        self.moderado_por = moderador
        self.fecha_moderacion = timezone.now()
        self.save()
