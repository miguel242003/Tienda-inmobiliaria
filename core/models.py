from django.db import models
from django.utils import timezone
from django.db.models import Sum


class ContactSubmission(models.Model):
    """Modelo para almacenar envíos del formulario de contacto"""
    
    ASUNTO_CHOICES = [
        ('', 'Selecciona un asunto'),
        ('consulta_general', 'Consulta General'),
        ('alquiler', 'Alquiler'),
        ('alquiler_temporal', 'Alquiler Temporal'),
        ('venta', 'Venta'),
        ('consorcio', 'Consorcio'),
        ('tasacion', 'Tasación de Propiedad'),
        ('inversion', 'Inversión Inmobiliaria'),
        ('financiamiento', 'Financiamiento Hipotecario'),
        ('administracion', 'Administración de Propiedades'),
        ('legal', 'Asesoría Legal'),
        ('mantenimiento', 'Mantenimiento y Reparaciones'),
        ('seguros', 'Seguros Inmobiliarios'),
        ('otro', 'Otro'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    email = models.EmailField(verbose_name="Email")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    asunto = models.CharField(max_length=30, choices=ASUNTO_CHOICES, verbose_name="Asunto")
    mensaje = models.TextField(verbose_name="Mensaje")
    fecha_envio = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Envío")
    
    class Meta:
        verbose_name = "Envío de Contacto"
        verbose_name_plural = "Envíos de Contacto"
        ordering = ['-fecha_envio']
    
    def __str__(self):
        return f"{self.nombre} - {self.get_asunto_display()} ({self.fecha_envio.strftime('%d/%m/%Y')})"
    
    def get_asunto_display(self):
        """Retorna el display del asunto"""
        return dict(self.ASUNTO_CHOICES).get(self.asunto, self.asunto)


class CVSubmission(models.Model):
    """Modelo para almacenar CVs enviados por candidatos"""
    
    POSITION_CHOICES = [
        ('agente_inmobiliario', 'Agente Inmobiliario'),
        ('asesor_comercial', 'Asesor Comercial'),
        ('gerente_ventas', 'Gerente de Ventas'),
        ('administrativo', 'Personal Administrativo'),
        ('marketing', 'Especialista en Marketing'),
        ('contabilidad', 'Contabilidad'),
        ('legal', 'Asesoría Legal'),
        ('otro', 'Otra posición'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('sin_experiencia', 'Sin experiencia'),
        ('1-2', '1-2 años'),
        ('3-5', '3-5 años'),
        ('6-10', '6-10 años'),
        ('10+', 'Más de 10 años'),
    ]
    
    EDUCATION_CHOICES = [
        ('secundario', 'Secundario Completo'),
        ('terciario', 'Terciario'),
        ('universitario', 'Universitario'),
        ('posgrado', 'Posgrado'),
    ]
    
    # Información personal
    nombre_completo = models.CharField(max_length=200, verbose_name="Nombre Completo")
    email = models.EmailField(verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    
    # Información profesional
    posicion_interes = models.CharField(
        max_length=50, 
        choices=POSITION_CHOICES, 
        verbose_name="Posición de Interés"
    )
    anos_experiencia = models.CharField(
        max_length=20, 
        choices=EXPERIENCE_CHOICES, 
        blank=True, 
        null=True, 
        verbose_name="Años de Experiencia"
    )
    nivel_educativo = models.CharField(
        max_length=20, 
        choices=EDUCATION_CHOICES, 
        blank=True, 
        null=True, 
        verbose_name="Nivel Educativo"
    )
    
    # Archivos
    cv_file = models.FileField(
        upload_to='cvs/%Y/%m/%d/', 
        verbose_name="Archivo CV",
        help_text="Formatos aceptados: PDF, DOC, DOCX"
    )
    carta_presentacion = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Carta de Presentación"
    )
    
    # Metadatos
    fecha_envio = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Envío")
    procesado = models.BooleanField(default=False, verbose_name="Procesado")
    notas_admin = models.TextField(blank=True, null=True, verbose_name="Notas del Administrador")
    
    class Meta:
        verbose_name = "CV Enviado"
        verbose_name_plural = "CVs Enviados"
        ordering = ['-fecha_envio']
    
    def __str__(self):
        return f"CV de {self.nombre_completo} - {self.get_posicion_interes_display()}"
    
    def get_file_size(self):
        """Retorna el tamaño del archivo en formato legible"""
        if self.cv_file:
            try:
                size = self.cv_file.size
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size < 1024.0:
                        return f"{size:.1f} {unit}"
                    size /= 1024.0
            except (FileNotFoundError, OSError):
                return "Archivo no encontrado"
        return "N/A"
    
    def get_file_extension(self):
        """Retorna la extensión del archivo"""
        if self.cv_file:
            return self.cv_file.name.split('.')[-1].upper()
        return "N/A"


class FormularioCount(models.Model):
    """Modelo para contar formularios enviados por mes"""
    
    TIPO_FORMULARIO_CHOICES = [
        ('contacto', 'Formulario de Contacto'),
        ('consulta_propiedad', 'Consulta de Propiedad'),
        ('cv', 'Formulario de CV'),
    ]
    
    tipo_formulario = models.CharField(
        max_length=20, 
        choices=TIPO_FORMULARIO_CHOICES,
        verbose_name="Tipo de Formulario"
    )
    año = models.IntegerField(verbose_name="Año")
    mes = models.IntegerField(verbose_name="Mes")  # 1-12
    cantidad = models.PositiveIntegerField(default=0, verbose_name="Cantidad")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    class Meta:
        verbose_name = "Conteo de Formulario"
        verbose_name_plural = "Conteos de Formularios"
        unique_together = ['tipo_formulario', 'año', 'mes']
        ordering = ['-año', '-mes', 'tipo_formulario']
    
    def __str__(self):
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        return f"{self.get_tipo_formulario_display()} - {meses[self.mes-1]} {self.año}: {self.cantidad}"
    
    @classmethod
    def incrementar_conteo(cls, tipo_formulario):
        """Incrementa el conteo para el tipo de formulario en el mes actual"""
        now = timezone.now()
        año_actual = now.year
        mes_actual = now.month
        
        # Obtener o crear el registro para este mes
        conteo, created = cls.objects.get_or_create(
            tipo_formulario=tipo_formulario,
            año=año_actual,
            mes=mes_actual,
            defaults={'cantidad': 0}
        )
        
        # Incrementar el conteo
        conteo.cantidad += 1
        conteo.save()
        
        return conteo
    
    @classmethod
    def obtener_conteo_mensual(cls, tipo_formulario, año=None, mes=None):
        """Obtiene el conteo para un tipo de formulario en un mes específico"""
        if año is None:
            año = timezone.now().year
        if mes is None:
            mes = timezone.now().month
            
        try:
            conteo = cls.objects.get(
                tipo_formulario=tipo_formulario,
                año=año,
                mes=mes
            )
            return conteo.cantidad
        except cls.DoesNotExist:
            return 0
    
    @classmethod
    def obtener_conteo_total_mes_actual(cls):
        """Obtiene el conteo total de todos los formularios en el mes actual"""
        now = timezone.now()
        conteos = cls.objects.filter(año=now.year, mes=now.month)
        return sum(conteo.cantidad for conteo in conteos)
    
    @classmethod
    def obtener_estadisticas_mensuales(cls, año=None):
        """Obtiene estadísticas mensuales para un año específico"""
        if año is None:
            año = timezone.now().year
            
        estadisticas = {}
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        
        for mes in range(1, 13):
            conteos = cls.objects.filter(año=año, mes=mes)
            total_mes = sum(conteo.cantidad for conteo in conteos)
            
            estadisticas[mes] = {
                'nombre': meses[mes-1],
                'total': total_mes,
                'contacto': cls.obtener_conteo_mensual('contacto', año, mes),
                'consulta_propiedad': cls.obtener_conteo_mensual('consulta_propiedad', año, mes),
                'cv': cls.obtener_conteo_mensual('cv', año, mes),
            }
        
        return estadisticas
