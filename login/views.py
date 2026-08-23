from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.exceptions import ValidationError as DjangoValidationError
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.urls import reverse
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
import bleach
import re
import logging
from propiedades.models import Propiedad
from propiedades.forms import PropiedadForm
from propiedades.validators import validar_imagen
from .models import AdminCredentials, PasswordResetCode
from .forms import AdminCredentialsForm, NuevoUsuarioAdminForm
from .forms_2fa import TwoFactorVerifyForm, BackupCodeForm
from .forms_password_reset import PasswordResetRequestForm, PasswordResetVerifyForm

logger = logging.getLogger(__name__)

def configurar_admin(request):
    """Vista para configurar credenciales del administrador (solo primera vez)"""
    # Verificar si ya existen credenciales
    if AdminCredentials.objects.filter(activo=True).exists():
        messages.warning(request, 'Las credenciales del administrador ya están configuradas.')
        return redirect('login:admin_login')
    
    if request.method == 'POST':
        form = AdminCredentialsForm(request.POST, request.FILES)
        if form.is_valid():
            # Crear usuario administrador primero
            user = None
            credenciales = None
            try:
                user = User.objects.create_user(
                    username=form.cleaned_data['email'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['nombre'] or 'Administrador',
                    last_name=form.cleaned_data['apellido'] or '',
                    is_staff=True,
                    is_superuser=True
                )
                
                # Ahora crear AdminCredentials con la relación ya establecida
                credenciales = form.save(commit=False)
                credenciales.user = user
                credenciales.save()
                
                messages.success(request, f'¡Administrador configurado exitosamente! Ahora puedes acceder con {credenciales.email}')
                return redirect('login:admin_login')
                
            except Exception as e:
                # Limpiar si algo salió mal
                if credenciales and credenciales.pk:
                    credenciales.delete()
                if user and user.pk:
                    user.delete()
                logger.error(f"Error al configurar el administrador inicial: {e}", exc_info=True)
                messages.error(request, 'No se pudo crear el usuario administrador. Intenta nuevamente.')
    else:
        form = AdminCredentialsForm()
    
    context = {
        'form': form,
        'es_configuracion_inicial': True,
    }
    return render(request, 'login/configurar_admin.html', context)

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def admin_login(request):
    """
    Vista de login para administradores con credenciales seguras y 2FA.
    
    🔒 SEGURIDAD:
    - Rate limiting: Máximo 5 intentos por minuto por IP
    - Validación y sanitización de inputs
    - Protección contra ataques de fuerza bruta
    """
    # Si el usuario ya está autenticado, redirigir al dashboard
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('login:dashboard')
    
    # Verificar si existen credenciales configuradas
    if not AdminCredentials.objects.filter(activo=True).exists():
        messages.info(request, 'Primera vez: Necesitas configurar las credenciales del administrador.')
        return redirect('login:configurar_admin')
    
    if request.method == 'POST':
        # 🔒 SEGURIDAD: Validar y sanitizar inputs
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError as DjangoValidationError
        import bleach
        
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        totp_code = request.POST.get('totp_code', '').strip()
        backup_code = request.POST.get('backup_code', '').strip()
        
        # Validar email
        try:
            validate_email(email)
            email = bleach.clean(email)  # Sanitizar
        except DjangoValidationError:
            messages.error(request, 'Email inválido.')
            return render(request, 'login/admin_login.html')
        
        # Validar longitud de contraseña
        if len(password) < 8:
            messages.error(request, 'Credenciales inválidas.')
            return render(request, 'login/admin_login.html')
        
        try:
            # Buscar credenciales
            credenciales = AdminCredentials.objects.get(email=email, activo=True)
            
            # Verificar contraseña (contra el User vinculado, única fuente de verdad)
            if credenciales.check_password(password):
                # Si 2FA está habilitado, verificar código
                if credenciales.two_factor_enabled:
                    if totp_code:
                        # Verificar código TOTP
                        if credenciales.verify_totp(totp_code):
                            return complete_login(request, credenciales)
                        else:
                            messages.error(request, 'Código de verificación incorrecto.')
                    elif backup_code:
                        # Verificar código de respaldo
                        if credenciales.verify_backup_code(backup_code.upper()):
                            return complete_login(request, credenciales)
                        else:
                            messages.error(request, 'Código de respaldo incorrecto o ya utilizado.')
                    else:
                        # 🔒 SEGURIDAD: NO devolver password en el contexto
                        messages.error(request, 'Se requiere código de verificación de 2FA.')
                        return render(request, 'login/admin_login.html', {
                            'email': email,
                            'show_2fa': True,
                            'requires_2fa': True
                        })
                else:
                    # Sin 2FA, proceder con login normal
                    return complete_login(request, credenciales)
            else:
                messages.error(request, 'Correo o contraseña incorrectos.')
                
        except AdminCredentials.DoesNotExist:
            messages.error(request, 'Correo o contraseña incorrectos.')
        except Exception as e:
            logger.error(f"Error inesperado en admin_login: {e}", exc_info=True)
            messages.error(request, 'Ocurrió un error inesperado. Intenta nuevamente.')
    
    return render(request, 'login/admin_login.html')

def complete_login(request, credenciales):
    """Completa el proceso de login después de verificar credenciales y 2FA.

    credenciales.user siempre existe: AdminCredentials.user es un
    OneToOneField obligatorio, así que no hace falta buscar ni crear un User
    acá (a diferencia de versiones anteriores de esta función)."""
    try:
        login(request, credenciales.user)
        nombre_completo = credenciales.get_nombre_completo()
        messages.success(request, f'¡Bienvenido, {nombre_completo}!')
        return redirect('login:dashboard')

    except Exception as e:
        logger.error(f"Error al completar el login: {e}", exc_info=True)
        messages.error(request, 'No se pudo completar el inicio de sesión. Intenta nuevamente.')
        return redirect('login:admin_login')

@login_required
def setup_2fa(request):
    """Vista para configurar 2FA"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('core:home')
    
    try:
        credenciales = request.user.admincredentials
    except AdminCredentials.DoesNotExist:
        messages.error(request, 'No se encontraron credenciales de administrador.')
        return redirect('login:admin_login')
    
    # Generar QR code si no existe
    if not credenciales.totp_secret:
        credenciales.generate_totp_secret()
        credenciales.save()
    
    if request.method == 'POST':
        from .forms_2fa import TwoFactorSetupForm
        form = TwoFactorSetupForm(request.POST)
        
        if form.is_valid():
            totp_code = form.cleaned_data['totp_code']
            
            # Verificar el código TOTP
            if credenciales.verify_totp(totp_code):
                # Habilitar 2FA
                credenciales.enable_2fa()
                messages.success(request, '¡2FA habilitado exitosamente!')
                return redirect('login:2fa_success')
            else:
                messages.error(request, 'Código de verificación incorrecto. Intenta de nuevo.')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        from .forms_2fa import TwoFactorSetupForm
        form = TwoFactorSetupForm()
    
    qr_code = credenciales.get_qr_code()
    totp_uri = credenciales.get_totp_uri()
    
    context = {
        'form': form,
        'qr_code': qr_code,
        'totp_uri': totp_uri,
        'credenciales': credenciales
    }
    
    return render(request, 'login/setup_2fa.html', context)

@login_required
def disable_2fa(request):
    """Vista para deshabilitar 2FA"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('core:home')
    
    try:
        credenciales = request.user.admincredentials
    except AdminCredentials.DoesNotExist:
        messages.error(request, 'No se encontraron credenciales de administrador.')
        return redirect('login:admin_login')
    
    if request.method == 'POST':
        credenciales.disable_2fa()
        messages.success(request, '2FA deshabilitado exitosamente.')
        return redirect('login:dashboard')
    
    return render(request, 'login/disable_2fa.html', {'credenciales': credenciales})

@login_required
def two_factor_success(request):
    """Vista de éxito después de configurar 2FA"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('core:home')
    
    try:
        credenciales = request.user.admincredentials
        backup_codes = credenciales.backup_codes
    except AdminCredentials.DoesNotExist:
        messages.error(request, 'No se encontraron credenciales de administrador.')
        return redirect('login:admin_login')
    
    context = {
        'credenciales': credenciales,
        'backup_codes': backup_codes
    }
    
    return render(request, 'login/2fa_success.html', context)

@login_required
def dashboard(request):
    """Dashboard del administrador"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('core:home')
    
    # Optimizar la consulta del usuario para incluir AdminCredentials
    # No reasignar request.user, solo obtener los datos necesarios
    user_with_credentials = User.objects.select_related('admincredentials').get(id=request.user.id)
    
    # Obtener estadísticas básicas
    total_users = User.objects.count()
    staff_users = User.objects.filter(is_staff=True).count()
    total_propiedades = Propiedad.objects.count()
    
    # Obtener conteos de formularios del mes actual
    from core.models import FormularioCount
    total_formularios_mes = FormularioCount.obtener_conteo_total_mes_actual()
    formularios_contacto = FormularioCount.obtener_conteo_mensual('contacto')
    formularios_consulta_propiedad = FormularioCount.obtener_conteo_mensual('consulta_propiedad')
    formularios_cv = FormularioCount.obtener_conteo_mensual('cv')
    
    # Obtener estadísticas del mes anterior para comparación
    from datetime import datetime
    now = timezone.now()
    if now.month == 1:
        mes_anterior = 12
        año_anterior = now.year - 1
    else:
        mes_anterior = now.month - 1
        año_anterior = now.year
    
    total_formularios_mes_anterior = 0
    for tipo in ['contacto', 'consulta_propiedad', 'cv']:
        total_formularios_mes_anterior += FormularioCount.obtener_conteo_mensual(tipo, año_anterior, mes_anterior)
    
    # Calcular porcentaje de cambio
    if total_formularios_mes_anterior > 0:
        cambio_porcentaje = round(((total_formularios_mes - total_formularios_mes_anterior) / total_formularios_mes_anterior) * 100)
    else:
        cambio_porcentaje = 0 if total_formularios_mes == 0 else 100
    
    # Obtener propiedades recientes
    propiedades_recientes = Propiedad.objects.all().order_by('-fecha_creacion')[:5]
    
    # Obtener CVs recientes
    from core.models import CVSubmission
    cvs_recientes = CVSubmission.objects.all().order_by('-fecha_envio')[:10]
    
    # Obtener todas las propiedades disponibles para el selector del gráfico
    # Excluir propiedades eliminadas (solo mostrar las que existen)
    todas_propiedades = Propiedad.objects.all().order_by('titulo')
    
    # Importar el formulario para el modal
    from propiedades.forms import PropiedadForm
    from propiedades.models import Amenidad
    form = PropiedadForm()
    
    # Obtener amenidades para el template
    amenidades = Amenidad.objects.all().order_by('nombre')
    
    # Obtener estadísticas de clics
    from propiedades.models import ClickPropiedad
    from datetime import datetime, timedelta
    
    # Total de clics (excluir propiedades eliminadas)
    total_clicks = ClickPropiedad.objects.filter(
        propiedad__isnull=False  # Excluir clics de propiedades eliminadas
    ).count()
    
    # Clics por mes (año actual completo: enero a diciembre)
    clicks_por_mes = []
    meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                     'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    # Mostrar los 12 meses del año actual (2025: enero a diciembre)
    año_actual = now.year
    
    for mes in range(1, 13):  # Del 1 al 12 (enero a diciembre)
        # Crear fechas de inicio y fin del mes
        fecha_inicio = timezone.datetime(año_actual, mes, 1)
        if mes == 12:
            fecha_fin = timezone.datetime(año_actual + 1, 1, 1)
        else:
            fecha_fin = timezone.datetime(año_actual, mes + 1, 1)
        
        # Convertir a timezone aware
        fecha_inicio = timezone.make_aware(fecha_inicio)
        fecha_fin = timezone.make_aware(fecha_fin)
        
        clicks_mes = ClickPropiedad.objects.filter(
            fecha_click__gte=fecha_inicio,
            fecha_click__lt=fecha_fin,
            propiedad__isnull=False  # Excluir clics de propiedades eliminadas
        ).count()
        
        clicks_por_mes.append({
            'mes': meses_nombres[mes - 1],
            'clicks': clicks_mes
        })
    
    # Clics por propiedad - Optimizado con una sola consulta
    clicks_por_propiedad = {}
    
    # Obtener todos los clics del año actual de una vez
    fecha_inicio_año = timezone.datetime(año_actual, 1, 1)
    fecha_fin_año = timezone.datetime(año_actual + 1, 1, 1)
    fecha_inicio_año = timezone.make_aware(fecha_inicio_año)
    fecha_fin_año = timezone.make_aware(fecha_fin_año)
    
    # Consulta optimizada: obtener todos los clics del año agrupados por propiedad y mes
    from django.db.models import Count
    from django.db.models.functions import Extract
    
    # Usar una consulta más simple sin Extract
    # Filtrar solo clics de propiedades que existen (excluir propiedades eliminadas)
    clicks_agrupados = ClickPropiedad.objects.filter(
        fecha_click__gte=fecha_inicio_año,
        fecha_click__lt=fecha_fin_año,
        propiedad__isnull=False  # Asegurar que la propiedad existe
    ).values('propiedad_id').annotate(
        total_clicks=Count('id')
    ).order_by('propiedad_id')
    
    # Inicializar todas las propiedades con datos en cero
    for propiedad in todas_propiedades:
        clicks_por_propiedad[propiedad.id] = {
            'clicks_totales': 0,
            'clicks_por_mes': [0] * 12  # 12 meses inicializados en 0
        }
    
    # Procesar los datos agrupados
    # Obtener IDs de propiedades existentes para filtrar
    ids_propiedades_existentes = set(todas_propiedades.values_list('id', flat=True))
    
    for click_data in clicks_agrupados:
        prop_id = click_data['propiedad_id']
        total = click_data['total_clicks']
        
        # Solo procesar si la propiedad existe
        if prop_id in ids_propiedades_existentes and prop_id in clicks_por_propiedad:
            # Asignar todos los clics al mes actual (octubre = mes 9, índice 9)
            mes_actual = timezone.now().month - 1  # Convertir a índice 0-based
            clicks_por_propiedad[prop_id]['clicks_por_mes'][mes_actual] = total
            clicks_por_propiedad[prop_id]['clicks_totales'] = total
    
    # Convertir clicks_por_propiedad a JSON para el template
    import json
    clicks_por_propiedad_json = json.dumps(clicks_por_propiedad)
    
    context = {
        'total_users': total_users,
        'staff_users': staff_users,
        'total_propiedades': total_propiedades,
        'propiedades_recientes': propiedades_recientes,
        'cvs_recientes': cvs_recientes,
        'todas_propiedades': todas_propiedades,
        'total_clicks': total_clicks,
        'clicks_por_mes': clicks_por_mes,
        'clicks_por_propiedad': clicks_por_propiedad_json,
        'form': form,
        'amenidades': amenidades,
        # Conteos de formularios
        'total_formularios_mes': total_formularios_mes,
        'formularios_contacto': formularios_contacto,
        'formularios_consulta_propiedad': formularios_consulta_propiedad,
        'formularios_cv': formularios_cv,
        'cambio_porcentaje': cambio_porcentaje,
    }
    
    return render(request, 'login/dashboard.html', context)

@login_required
def dashboard_clicks_data(request):
    """Endpoint AJAX para obtener datos actualizados de clics"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'No tienes permisos'}, status=403)
    
    try:
        from propiedades.models import ClickPropiedad
        from datetime import datetime
        import json
        
        # Obtener todas las propiedades existentes (excluir eliminadas)
        todas_propiedades = Propiedad.objects.all().order_by('titulo')
        
        # Obtener estadísticas de clics (excluir propiedades eliminadas)
        total_clicks = ClickPropiedad.objects.filter(
            propiedad__isnull=False  # Excluir clics de propiedades eliminadas
        ).count()
        
        # Clics por mes (año actual completo: enero a diciembre)
        clicks_por_mes = []
        meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                         'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        
        # Mostrar los 12 meses del año actual
        now = timezone.now()
        año_actual = now.year
        
        for mes in range(1, 13):  # Del 1 al 12 (enero a diciembre)
            # Crear fechas de inicio y fin del mes
            fecha_inicio = timezone.datetime(año_actual, mes, 1)
            if mes == 12:
                fecha_fin = timezone.datetime(año_actual + 1, 1, 1)
            else:
                fecha_fin = timezone.datetime(año_actual, mes + 1, 1)
            
            # Convertir a timezone aware
            fecha_inicio = timezone.make_aware(fecha_inicio)
            fecha_fin = timezone.make_aware(fecha_fin)
            
            clicks_mes = ClickPropiedad.objects.filter(
                fecha_click__gte=fecha_inicio,
                fecha_click__lt=fecha_fin
            ).count()
            
            clicks_por_mes.append({
                'mes': meses_nombres[mes - 1],
                'clicks': clicks_mes
            })
        
        # Clics por propiedad - Optimizado con una sola consulta
        clicks_por_propiedad = {}
        
        # Obtener todos los clics del año actual de una vez
        fecha_inicio_año = timezone.datetime(año_actual, 1, 1)
        fecha_fin_año = timezone.datetime(año_actual + 1, 1, 1)
        fecha_inicio_año = timezone.make_aware(fecha_inicio_año)
        fecha_fin_año = timezone.make_aware(fecha_fin_año)
        
        # Consulta optimizada: obtener todos los clics del año agrupados por propiedad
        from django.db.models import Count
        
        clicks_agrupados = ClickPropiedad.objects.filter(
            fecha_click__gte=fecha_inicio_año,
            fecha_click__lt=fecha_fin_año,
            propiedad__isnull=False  # Asegurar que la propiedad existe
        ).values('propiedad_id').annotate(
            total_clicks=Count('id')
        ).order_by('propiedad_id')
        
        # Inicializar todas las propiedades con datos en cero
        for propiedad in todas_propiedades:
            clicks_por_propiedad[propiedad.id] = {
                'clicks_totales': 0,
                'clicks_por_mes': [0] * 12  # 12 meses inicializados en 0
            }
        
        # Procesar los datos agrupados
        # Obtener IDs de propiedades existentes para filtrar
        ids_propiedades_existentes = set(todas_propiedades.values_list('id', flat=True))
        
        for click_data in clicks_agrupados:
            prop_id = click_data['propiedad_id']
            total = click_data['total_clicks']
            
            # Solo procesar si la propiedad existe
            if prop_id in ids_propiedades_existentes and prop_id in clicks_por_propiedad:
                # Asignar todos los clics al mes actual (octubre = mes 9, índice 9)
                mes_actual = timezone.now().month - 1  # Convertir a índice 0-based
                clicks_por_propiedad[prop_id]['clicks_por_mes'][mes_actual] = total
                clicks_por_propiedad[prop_id]['clicks_totales'] = total
        
        return JsonResponse({
            'success': True,
            'total_clicks': total_clicks,
            'clicks_por_mes': clicks_por_mes,
            'clicks_por_propiedad': clicks_por_propiedad
        })
        
    except Exception as e:
        logger.error(f"Error en dashboard_clicks_data: {e}", exc_info=True)
        return JsonResponse({
            'error': 'No se pudieron obtener los datos de clics.',
            'error_details': str(e) if settings.DEBUG else None,
        }, status=500)

def admin_logout(request):
    """Cerrar sesión del administrador"""
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('core:home')

@login_required
def gestionar_propiedades(request):
    """Vista para gestionar propiedades (listar, editar, eliminar)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('core:home')
    
    propiedades = Propiedad.objects.all().order_by('-fecha_creacion')
    
    context = {
        'propiedades': propiedades,
    }
    return render(request, 'login/gestionar_propiedades.html', context)

def _contexto_editar_propiedad(form, propiedad):
    from propiedades.models import Amenidad
    return {
        'form': form,
        'propiedad': propiedad,
        'titulo_pagina': 'Editar Propiedad',
        'amenidades': Amenidad.objects.all(),
    }


def _limpiar_imagenes_estaticas_antiguas(slug_antiguo):
    from core.utils import eliminar_imagenes_static_propiedad
    resultado = eliminar_imagenes_static_propiedad(slug_antiguo)
    if resultado['success']:
        logger.info(f"Imágenes estáticas antiguas eliminadas: {resultado['archivos_eliminados']}")
    else:
        logger.warning(f"No se pudieron eliminar todas las imágenes estáticas: {resultado['message']}")


@login_required
def editar_propiedad(request, propiedad_id):
    """Vista para editar una propiedad existente"""
    try:
        if not request.user.is_staff:
            messages.error(request, 'No tienes permisos para editar propiedades.')
            return redirect('core:home')

        propiedad = get_object_or_404(Propiedad, id=propiedad_id)

        if request.method != 'POST':
            form = PropiedadForm(instance=propiedad, is_edit=True)
            return render(request, 'login/editar_propiedad.html', _contexto_editar_propiedad(form, propiedad))

        es_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = PropiedadForm(request.POST, request.FILES, instance=propiedad, is_edit=True)

        if not form.is_valid():
            logger.warning(f"Formulario de edición no válido: {form.errors}")
            if es_ajax:
                errors = {field: [str(err) for err in field_errors] for field, field_errors in form.errors.items()}
                if form.non_field_errors():
                    errors['__all__'] = [str(err) for err in form.non_field_errors()]
                return JsonResponse({
                    'success': False,
                    'message': 'Por favor corrige los errores en el formulario.',
                    'errors': errors
                }, status=400)

            error_messages = [f'{field}: {error}' for field, errs in form.errors.items() for error in errs]
            messages.error(
                request,
                f'Errores encontrados: {"; ".join(error_messages)}' if error_messages
                else 'Por favor corrige los errores en el formulario.'
            )
            return render(request, 'login/editar_propiedad.html', _contexto_editar_propiedad(form, propiedad))

        # Referencia para saber si hay que limpiar imágenes estáticas viejas después de guardar
        slug_antiguo = propiedad.slug
        imagenes_cambiaron = 'imagen_principal' in request.FILES or 'imagen_secundaria' in request.FILES

        try:
            propiedad = form.save(commit=False)
            propiedad.save()
            form.save_m2m()
            propiedad.refresh_from_db()

            # El método save() del modelo ya copió las nuevas imágenes a static;
            # si cambiaron, hay que limpiar las versiones estáticas anteriores.
            if imagenes_cambiaron and slug_antiguo:
                _limpiar_imagenes_estaticas_antiguas(slug_antiguo)

        except Exception as e:
            logger.error(f"Error al guardar propiedad editada: {e}", exc_info=True)
            if es_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Error al guardar la propiedad.',
                    'error_details': str(e) if settings.DEBUG else None
                }, status=500)
            messages.error(request, 'Error al guardar la propiedad. Intenta nuevamente.')
            return render(request, 'login/editar_propiedad.html', _contexto_editar_propiedad(form, propiedad))

        # Eliminar fotos adicionales marcadas para borrar
        fotos_eliminar = request.POST.getlist('fotos_eliminar')
        if fotos_eliminar:
            from propiedades.models import FotoPropiedad
            FotoPropiedad.objects.filter(id__in=fotos_eliminar, propiedad=propiedad).delete()

        # Agregar fotos/videos nuevos, continuando la numeración existente
        from django.db.models import Max
        from propiedades.views import guardar_archivos_adicionales
        ultimo_orden = propiedad.fotos.aggregate(Max('orden'))['orden__max'] or 0
        guardar_archivos_adicionales(
            propiedad, request.FILES.getlist('fotos_adicionales'), orden_inicial=ultimo_orden
        )

        mensaje = f'Propiedad "{propiedad.titulo}" actualizada exitosamente.'
        messages.success(request, mensaje)

        if es_ajax:
            return JsonResponse({
                'success': True,
                'message': mensaje,
                'redirect_url': reverse('login:dashboard')
            })
        return redirect('login:dashboard')

    except Exception as e:
        logger.critical(f"Error crítico en editar_propiedad: {e}", exc_info=True)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Error inesperado al editar la propiedad.',
                'error_details': str(e) if settings.DEBUG else None
            }, status=500)

        messages.error(request, 'Ocurrió un error inesperado. Intenta nuevamente.')
        return redirect('login:dashboard')

@login_required
def eliminar_propiedad(request, propiedad_id):
    """Vista para eliminar una propiedad"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para eliminar propiedades.')
        return redirect('core:home')
    
    propiedad = get_object_or_404(Propiedad, id=propiedad_id)
    
    if request.method == 'POST':
        titulo = propiedad.titulo
        slug = propiedad.slug
        
        # Eliminar imágenes estáticas antes de eliminar la propiedad
        from core.utils import eliminar_imagenes_static_propiedad
        resultado = eliminar_imagenes_static_propiedad(slug)
        if resultado['success']:
            logger.info(f"Imágenes estáticas eliminadas: {resultado['archivos_eliminados']}")
        else:
            logger.warning(f"No se pudieron eliminar todas las imágenes estáticas: {resultado['message']}")
        
        propiedad.delete()
        messages.success(request, f'Propiedad "{titulo}" eliminada exitosamente.')
        return redirect('login:gestionar_propiedades')
    
    context = {
        'propiedad': propiedad,
    }
    return render(request, 'login/confirmar_eliminar_propiedad.html', context)

@login_required
def eliminar_propiedad_ajax(request, propiedad_id):
    """Vista AJAX para eliminar propiedad sin recargar página"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'No tienes permisos para eliminar propiedades.'})
    
    if request.method == 'POST':
        try:
            propiedad = get_object_or_404(Propiedad, id=propiedad_id)
            titulo = propiedad.titulo
            slug = propiedad.slug
            
            # Eliminar imágenes estáticas antes de eliminar la propiedad
            from core.utils import eliminar_imagenes_static_propiedad
            resultado = eliminar_imagenes_static_propiedad(slug)
            if resultado['success']:
                logger.info(f"Imágenes estáticas eliminadas: {resultado['archivos_eliminados']}")
            else:
                logger.warning(f"No se pudieron eliminar todas las imágenes estáticas: {resultado['message']}")

            propiedad.delete()
            return JsonResponse({
                'success': True,
                'message': f'Propiedad "{titulo}" eliminada exitosamente.',
                'propiedad_id': propiedad_id
            })
        except Exception as e:
            logger.error(f"Error al eliminar propiedad {propiedad_id}: {e}", exc_info=True)
            return JsonResponse({'success': False, 'message': 'No se pudo eliminar la propiedad.'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

@login_required
def actualizar_perfil(request):
    """Vista AJAX para actualizar el perfil del administrador"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'No tienes permisos para actualizar el perfil.'})

    if request.method == 'POST':
        try:
            # Buscar o crear AdminCredentials usando la nueva relación
            from .models import AdminCredentials
            try:
                admin_creds = request.user.admincredentials
            except AdminCredentials.DoesNotExist:
                admin_creds = AdminCredentials.objects.create(
                    user=request.user,
                    nombre=request.user.first_name or 'Administrador',
                    apellido=request.user.last_name or 'del Sistema',
                    email=request.user.email,
                    telefono='+52-1-33-00000000',
                )

            # Validar campos antes de actualizar
            nombre = request.POST.get('nombre', '').strip()
            apellido = request.POST.get('apellido', '').strip()

            # Validaciones para nombre
            if not nombre:
                return JsonResponse({'success': False, 'message': 'El nombre es obligatorio.'})
            elif len(nombre) < 2:
                return JsonResponse({'success': False, 'message': 'El nombre debe tener al menos 2 caracteres.'})
            elif len(nombre) > 50:
                return JsonResponse({'success': False, 'message': 'El nombre no puede tener más de 50 caracteres.'})
            elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
                return JsonResponse({'success': False, 'message': 'El nombre solo puede contener letras y espacios.'})

            # Validaciones para apellido
            if not apellido:
                return JsonResponse({'success': False, 'message': 'El apellido es obligatorio.'})
            elif len(apellido) < 2:
                return JsonResponse({'success': False, 'message': 'El apellido debe tener al menos 2 caracteres.'})
            elif len(apellido) > 50:
                return JsonResponse({'success': False, 'message': 'El apellido no puede tener más de 50 caracteres.'})
            elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', apellido):
                return JsonResponse({'success': False, 'message': 'El apellido solo puede contener letras y espacios.'})

            # Actualizar campos
            admin_creds.nombre = nombre
            admin_creds.apellido = apellido
            admin_creds.telefono = request.POST.get('telefono', admin_creds.telefono)

            # Fecha de nacimiento
            fecha_nacimiento = request.POST.get('fecha_nacimiento')
            if fecha_nacimiento:
                from datetime import datetime
                admin_creds.fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()

            # Foto de perfil
            if 'foto_perfil' in request.FILES:
                admin_creds.foto_perfil = request.FILES['foto_perfil']

            admin_creds.save()

            # Actualizar también el usuario de Django
            request.user.first_name = admin_creds.nombre
            request.user.last_name = admin_creds.apellido
            request.user.save()

            # Preparar respuesta
            response_data = {
                'success': True,
                'message': 'Perfil actualizado exitosamente.'
            }

            # Incluir URL de la foto si existe
            if admin_creds.foto_perfil:
                response_data['foto_url'] = admin_creds.foto_perfil.url

            return JsonResponse(response_data)

        except Exception as e:
            logger.error(f"Error al actualizar perfil: {e}", exc_info=True)
            return JsonResponse({'success': False, 'message': 'No se pudo actualizar el perfil.'})

    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

@login_required
@ratelimit(key='user', rate='10/h', method='POST', block=True)
def crear_nuevo_usuario_admin(request):
    """
    Vista AJAX para crear un nuevo usuario administrativo.
    
    🔒 SEGURIDAD:
    - Rate limiting: Máximo 10 creaciones por hora por usuario
    - Validación exhaustiva de todos los campos
    - Protección contra spam de usuarios
    """
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'No tienes permisos para crear usuarios administrativos.'})
    
    if request.method == 'POST':
        try:
            # Validar campos antes de procesar el formulario
            nombre = request.POST.get('nombre', '').strip()
            apellido = request.POST.get('apellido', '').strip()
            telefono = request.POST.get('telefono', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            confirmar_password = request.POST.get('confirmar_password', '')
            fecha_nacimiento = request.POST.get('fecha_nacimiento', '')
            
            # Validaciones para nombre
            if not nombre:
                return JsonResponse({'success': False, 'message': 'El nombre es obligatorio.'})
            elif len(nombre) < 2:
                return JsonResponse({'success': False, 'message': 'El nombre debe tener al menos 2 caracteres.'})
            elif len(nombre) > 50:
                return JsonResponse({'success': False, 'message': 'El nombre no puede tener más de 50 caracteres.'})
            elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
                return JsonResponse({'success': False, 'message': 'El nombre solo puede contener letras y espacios.'})
            
            # Validaciones para apellido
            if not apellido:
                return JsonResponse({'success': False, 'message': 'El apellido es obligatorio.'})
            elif len(apellido) < 2:
                return JsonResponse({'success': False, 'message': 'El apellido debe tener al menos 2 caracteres.'})
            elif len(apellido) > 50:
                return JsonResponse({'success': False, 'message': 'El apellido no puede tener más de 50 caracteres.'})
            elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', apellido):
                return JsonResponse({'success': False, 'message': 'El apellido solo puede contener letras y espacios.'})
            
            # Validaciones para teléfono
            if not telefono or telefono == '+54':
                return JsonResponse({'success': False, 'message': 'Debes ingresar el número de teléfono después del +54.'})
            elif not re.match(r'^\+54\d{10,12}$', telefono):
                return JsonResponse({'success': False, 'message': 'El teléfono debe tener entre 10 y 12 dígitos después del +54.'})
            
            # Validaciones para correo electrónico
            if not email:
                return JsonResponse({'success': False, 'message': 'El correo electrónico es obligatorio.'})
            elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                return JsonResponse({'success': False, 'message': 'Ingresa un correo electrónico válido.'})
            
            # Validaciones para contraseña
            if not password:
                return JsonResponse({'success': False, 'message': 'La contraseña es obligatoria.'})
            elif len(password) < 8:
                return JsonResponse({'success': False, 'message': 'La contraseña debe tener al menos 8 caracteres.'})
            
            # Validaciones para confirmar contraseña
            if not confirmar_password:
                return JsonResponse({'success': False, 'message': 'Debes confirmar la contraseña.'})
            elif password != confirmar_password:
                return JsonResponse({'success': False, 'message': 'Las contraseñas no coinciden.'})
            
            # Validaciones para fecha de nacimiento
            if fecha_nacimiento:
                from datetime import datetime
                try:
                    fecha_obj = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
                    min_fecha = datetime(1900, 1, 1).date()
                    año_actual = datetime.now().year
                    max_fecha = datetime(año_actual, 12, 31).date()
                    
                    if fecha_obj < min_fecha or fecha_obj > max_fecha:
                        return JsonResponse({'success': False, 'message': f'La fecha debe estar entre 1900 y {año_actual}.'})
                except ValueError:
                    return JsonResponse({'success': False, 'message': 'Formato de fecha inválido.'})
            
            form = NuevoUsuarioAdminForm(request.POST, request.FILES)

            if form.is_valid():
                # Crear usuario administrador primero
                try:
                    user = User.objects.create_user(
                        username=form.cleaned_data['email'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        first_name=form.cleaned_data['nombre'] or 'Administrador',
                        last_name=form.cleaned_data['apellido'] or '',
                        is_staff=True,
                        # No superuser: un admin creado desde el dashboard no debe tener
                        # acceso total al panel /admin/ y al ORM de Django por defecto.
                        is_superuser=False
                    )
                    
                    # Ahora crear AdminCredentials con la relación ya establecida
                    credenciales = form.save(commit=False)
                    credenciales.user = user
                    credenciales.save()
                    
                    # Convertir la fecha UTC a la zona horaria local
                    fecha_local = timezone.localtime(credenciales.fecha_creacion)
                    
                    return JsonResponse({
                        'success': True, 
                        'message': f'Usuario administrativo "{credenciales.get_nombre_completo()}" creado exitosamente.',
                        'usuario': {
                            'nombre': credenciales.get_nombre_completo(),
                            'email': credenciales.email,
                            'fecha_creacion': fecha_local.strftime('%d/%m/%Y %H:%M')
                        }
                    })
                    
                except Exception as e:
                    # 'credenciales' puede no existir todavía si el fallo ocurrió al crear el User
                    if 'credenciales' in locals() and credenciales and credenciales.pk:
                        credenciales.delete()
                    logger.error(f"Error al crear usuario administrativo: {e}", exc_info=True)
                    return JsonResponse({'success': False, 'message': 'No se pudo crear el usuario administrativo.'})
            else:
                # Recopilar errores del formulario
                errors = {}
                for field, field_errors in form.errors.items():
                    errors[field] = [str(error) for error in field_errors]

                return JsonResponse({
                    'success': False,
                    'message': 'Por favor corrige los errores en el formulario.',
                    'errors': errors
                })

        except Exception as e:
            logger.error(f"Error al procesar creación de usuario administrativo: {e}", exc_info=True)
            return JsonResponse({'success': False, 'message': 'No se pudo procesar la solicitud.'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

@login_required
def contar_usuarios_admin(request):
    """Vista temporal para contar usuarios administrativos"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'No tienes permisos.'})
    
    try:
        # Contar AdminCredentials activos
        admin_creds_count = AdminCredentials.objects.filter(activo=True).count()
        
        # Contar usuarios staff
        staff_users_count = User.objects.filter(is_staff=True).count()
        
        # Obtener detalles de AdminCredentials
        admin_creds_details = []
        for cred in AdminCredentials.objects.filter(activo=True):
            admin_creds_details.append({
                'nombre': cred.get_nombre_completo(),
                'email': cred.email,
                'fecha_creacion': cred.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                'activo': cred.activo
            })
        
        # Obtener detalles de usuarios staff
        staff_users_details = []
        for user in User.objects.filter(is_staff=True):
            staff_users_details.append({
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined.strftime('%d/%m/%Y %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'admin_credentials_count': admin_creds_count,
            'staff_users_count': staff_users_count,
            'admin_credentials_details': admin_creds_details,
            'staff_users_details': staff_users_details
        })
        
    except Exception as e:
        logger.error(f"Error en contar_usuarios_admin: {e}", exc_info=True)
        return JsonResponse({'success': False, 'message': 'No se pudieron obtener los datos.'})

@login_required
def cambiar_password(request):
    """Vista para cambiar la contraseña del usuario"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'No tienes permisos.'})
    
    if request.method == 'POST':
        try:
            password_actual = request.POST.get('password_actual')
            nueva_password = request.POST.get('nueva_password')
            confirmar_password = request.POST.get('confirmar_nueva_password')

            # Validaciones básicas
            if not nueva_password or not confirmar_password:
                return JsonResponse({'success': False, 'message': 'Por favor completa todos los campos.'})

            if nueva_password != confirmar_password:
                return JsonResponse({'success': False, 'message': 'Las contraseñas no coinciden.'})

            if len(nueva_password) < 8:
                return JsonResponse({'success': False, 'message': 'La contraseña debe tener al menos 8 caracteres.'})

            # Verificar contraseña actual (User es la única fuente de verdad para el login)
            if not password_actual:
                return JsonResponse({'success': False, 'message': 'Debes ingresar tu contraseña actual.'})

            if not request.user.check_password(password_actual):
                return JsonResponse({'success': False, 'message': 'La contraseña actual es incorrecta.'})

            # Cambiar contraseña en User (única fuente de verdad) y mantener la sesión activa
            from django.contrib.auth import update_session_auth_hash
            request.user.set_password(nueva_password)
            request.user.save()
            update_session_auth_hash(request, request.user)

            return JsonResponse({'success': True, 'message': 'Contraseña cambiada exitosamente.'})
            
        except Exception as e:
            logger.error(f"Error al cambiar la contraseña: {e}", exc_info=True)
            return JsonResponse({'success': False, 'message': 'No se pudo cambiar la contraseña.'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

@login_required
def enviar_codigo_sms(request):
    """Vista para enviar código de verificación por SMS"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'No tienes permisos.'})
    
    # Verificación de contraseña por SMS: todavía no hay un proveedor de SMS
    # (ej. Twilio) integrado. Antes esta vista generaba un código y respondía
    # "success" sin enviar nada realmente, lo cual era engañoso para quien
    # usa el botón en el dashboard. Hasta que se integre un proveedor real,
    # se responde con un error claro; el frontend ya maneja ese caso
    # (mostrarMensajePassword con el mensaje de error) sin cambios.
    return JsonResponse({
        'success': False,
        'message': 'La verificación por SMS todavía no está disponible. Usa tu contraseña actual para cambiarla.',
    })

@login_required
def verificar_codigo_sms(request):
    """Vista para verificar el código SMS.

    Ver enviar_codigo_sms: sin proveedor de SMS integrado, nunca se genera
    un código real, así que esta vista siempre responde que no hay nada
    pendiente. Se mantiene el endpoint (el dashboard ya lo llama) en vez de
    romper esa pantalla, pero de forma honesta.
    """
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'No tienes permisos.'})

    return JsonResponse({
        'success': False,
        'message': 'La verificación por SMS todavía no está disponible.',
    })

@login_required
def listar_usuarios_admin(request):
    """Vista para listar todos los usuarios administrativos"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'No tienes permisos.'})
    
    try:
        # Obtener todos los usuarios administrativos
        usuarios = AdminCredentials.objects.filter(activo=True).select_related('user')
        
        usuarios_data = []
        for cred in usuarios:
            # Convertir la fecha UTC a la zona horaria local
            fecha_local = timezone.localtime(cred.fecha_creacion)
            usuarios_data.append({
                'id': cred.id,
                'nombre_completo': cred.get_nombre_completo(),
                'email': cred.email,
                'telefono': cred.telefono or 'No registrado',
                'fecha_creacion': fecha_local.strftime('%d/%m/%Y %H:%M'),
                'activo': cred.activo,
                'foto_perfil': cred.get_foto_perfil_url()
            })
        
        return JsonResponse({
            'success': True,
            'usuarios': usuarios_data
        })
        
    except Exception as e:
        logger.error(f"Error al listar usuarios administrativos: {e}", exc_info=True)
        return JsonResponse({'success': False, 'message': 'No se pudieron listar los usuarios.'})

@login_required
def eliminar_usuario_admin(request, usuario_id):
    """Vista para eliminar un usuario administrativo"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'No tienes permisos.'})
    
    if request.method == 'POST':
        try:
            # Verificar que no se esté eliminando a sí mismo
            if request.user.admincredentials.id == usuario_id:
                return JsonResponse({'success': False, 'message': 'No puedes eliminar tu propia cuenta.'})
            
            # Buscar las credenciales del usuario
            try:
                admin_creds = AdminCredentials.objects.get(id=usuario_id, activo=True)
            except AdminCredentials.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Usuario no encontrado.'})
            
            # Obtener el usuario asociado
            user = admin_creds.user
            
            # Eliminar las credenciales (esto también eliminará el usuario por CASCADE)
            admin_creds.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Usuario {admin_creds.get_nombre_completo()} eliminado exitosamente.'
            })
            
        except Exception as e:
            logger.error(f"Error al eliminar usuario administrativo: {e}", exc_info=True)
            return JsonResponse({'success': False, 'message': 'No se pudo eliminar el usuario.'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

@login_required
def gestionar_resenas(request):
    """Vista para gestionar reseñas en el dashboard admin"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'No tienes permisos.'})
    
    try:
        from propiedades.models import Resena
        
        # Verificar si solo se solicitan estadísticas
        solo_estadisticas = request.GET.get('estadisticas') == 'true'
        
        if solo_estadisticas:
            # Solo devolver estadísticas
            total_espera = Resena.objects.filter(estado='pendiente').count()
            total_aceptadas = Resena.objects.filter(estado='aprobada').count()
            total_rechazadas = Resena.objects.filter(estado='rechazada').count()
            
            return JsonResponse({
                'success': True,
                'estadisticas': {
                    'en_espera': total_espera,
                    'aceptadas': total_aceptadas,
                    'rechazadas': total_rechazadas,
                    'total': total_espera + total_aceptadas + total_rechazadas
                }
            })
        
        # Obtener parámetros de paginación y filtros
        page = int(request.GET.get('page', 1))
        per_page = 5
        start = (page - 1) * per_page
        end = start + per_page
        
        # Obtener filtros
        filtro_estado = request.GET.get('estado', 'todos')
        filtro_propiedad = request.GET.get('propiedad', 'todas')
        filtro_calificacion = request.GET.get('calificacion', 'todas')
        
        # Construir queryset base
        resenas = Resena.objects.all().select_related('propiedad').order_by('-fecha_creacion')
        
        # Aplicar filtros
        if filtro_estado != 'todos':
            if filtro_estado == 'pendiente':
                resenas = resenas.filter(estado='pendiente')
            elif filtro_estado == 'aprobada':
                resenas = resenas.filter(estado='aprobada')
            elif filtro_estado == 'rechazada':
                resenas = resenas.filter(estado='rechazada')
        # Si filtro_estado == 'todos', mostrar todas las reseñas (incluyendo rechazadas)
        
        if filtro_propiedad != 'todas':
            resenas = resenas.filter(propiedad_id=filtro_propiedad)
        
        if filtro_calificacion != 'todas':
            resenas = resenas.filter(calificacion=int(filtro_calificacion))
        total_resenas = resenas.count()
        resenas_paginadas = resenas[start:end]
        
        resenas_data = []
        for resena in resenas_paginadas:
            resenas_data.append({
                'id': resena.id,
                'propiedad_titulo': resena.propiedad.titulo,
                'propiedad_id': resena.propiedad.id,
                'nombre_usuario': resena.nombre_usuario,
                'email_usuario': resena.email_usuario,
                'calificacion': resena.calificacion,
                'titulo': resena.titulo,
                'comentario': resena.comentario,
                'fecha_creacion': resena.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                'estado': resena.get_estado_display(),
                'estrellas_html': resena.get_estrellas_html()
            })
        
        # Calcular información de paginación
        total_pages = (total_resenas + per_page - 1) // per_page
        has_previous = page > 1
        has_next = page < total_pages
        
        # Incluir estadísticas en la respuesta
        total_espera = Resena.objects.filter(estado='pendiente').count()
        total_aceptadas = Resena.objects.filter(estado='aprobada').count()
        total_rechazadas = Resena.objects.filter(estado='rechazada').count()
        
        return JsonResponse({
            'success': True,
            'resenas': resenas_data,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_resenas': total_resenas,
                'per_page': per_page,
                'has_previous': has_previous,
                'has_next': has_next,
                'previous_page': page - 1 if has_previous else None,
                'next_page': page + 1 if has_next else None
            },
            'estadisticas': {
                'en_espera': total_espera,
                'aceptadas': total_aceptadas,
                'rechazadas': total_rechazadas,
                'total': total_espera + total_aceptadas + total_rechazadas
            }
        })
        
    except Exception as e:
        logger.error(f"Error al cargar reseñas: {e}", exc_info=True)
        return JsonResponse({'success': False, 'message': 'No se pudieron cargar las reseñas.'})

@login_required
def eliminar_resena(request):
    """Vista para eliminar una reseña permanentemente"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'No tienes permisos para eliminar reseñas.'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido.'})
    
    try:
        import json
        data = json.loads(request.body)
        resena_id = data.get('resena_id')
        
        if not resena_id:
            return JsonResponse({'success': False, 'message': 'ID de reseña no proporcionado.'})
        
        from propiedades.models import Resena
        resena = get_object_or_404(Resena, id=resena_id)
        
        # Verificar que la reseña esté aprobada o rechazada (no pendiente)
        if resena.estado == 'pendiente':
            return JsonResponse({'success': False, 'message': 'No se puede eliminar una reseña pendiente. Primero debe ser aprobada o rechazada.'})
        
        # Eliminar la reseña
        resena.delete()
        
        return JsonResponse({
            'success': True, 
            'message': 'Reseña eliminada exitosamente.'
        })
        
    except Exception as e:
        logger.error(f"Error al eliminar reseña: {e}", exc_info=True)
        return JsonResponse({'success': False, 'message': 'No se pudo eliminar la reseña.'})

@login_required
def aprobar_resena(request, resena_id):
    """Vista para aprobar una reseña"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'No tienes permisos.'})
    
    if request.method == 'POST':
        try:
            from propiedades.models import Resena
            
            resena = Resena.objects.get(id=resena_id, estado='pendiente')
            resena.aprobar(request.user.admincredentials)
            
            return JsonResponse({
                'success': True,
                'message': f'Reseña de {resena.nombre_usuario} aprobada exitosamente.'
            })
            
        except Resena.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Reseña no encontrada.'})
        except Exception as e:
            logger.error(f"Error al aprobar reseña: {e}", exc_info=True)
            return JsonResponse({'success': False, 'message': 'No se pudo aprobar la reseña.'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

@login_required
def rechazar_resena(request, resena_id):
    """Vista para rechazar una reseña"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'No tienes permisos.'})
    
    if request.method == 'POST':
        try:
            from propiedades.models import Resena
            
            resena = Resena.objects.get(id=resena_id, estado='pendiente')
            resena.rechazar(request.user.admincredentials)
            
            return JsonResponse({
                'success': True,
                'message': f'Reseña de {resena.nombre_usuario} rechazada.'
            })
            
        except Resena.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Reseña no encontrada.'})
        except Exception as e:
            logger.error(f"Error al rechazar reseña: {e}", exc_info=True)
            return JsonResponse({'success': False, 'message': 'No se pudo rechazar la reseña.'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


# ========================================
# VISTAS PARA RECUPERACIÓN DE CONTRASEÑA
# ========================================

def password_reset_request(request):
    """Vista para solicitar recuperación de contraseña"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('login:dashboard')
    
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            try:
                # Generar código de recuperación
                reset_code = PasswordResetCode.generate_code(email)
                
                # Enviar email con el código
                send_password_reset_email(email, reset_code.code)
                
                messages.success(request, f'Se ha enviado un código de verificación a {email}. Revisa tu correo electrónico.')
                return redirect('login:password_reset_verify', email=email)
                
            except Exception as e:
                logger.error(f"Error al enviar email de recuperación de contraseña: {e}", exc_info=True)
                messages.error(request, 'No se pudo enviar el código de verificación. Intenta nuevamente.')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'login/password_reset_request.html', {'form': form})


def password_reset_verify(request, email):
    """Vista para verificar código y cambiar contraseña"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('login:dashboard')
    
    # Verificar que existe un código válido para este email
    try:
        reset_code = PasswordResetCode.objects.filter(email=email, used=False).first()
        if not reset_code or not reset_code.is_valid():
            messages.error(request, 'El código de recuperación ha expirado o no es válido.')
            return redirect('login:password_reset_request')
    except Exception:
        messages.error(request, 'Error al verificar el código.')
        return redirect('login:password_reset_request')
    
    if request.method == 'POST':
        form = PasswordResetVerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            new_password = form.cleaned_data['new_password']
            
            # Verificar el código
            if reset_code.code == code:
                try:
                    # Obtener las credenciales del administrador (credenciales.user
                    # siempre existe: es un OneToOneField obligatorio)
                    credenciales = AdminCredentials.objects.get(email=email, activo=True)

                    credenciales.user.set_password(new_password)
                    credenciales.user.save()

                    # Marcar el código como usado
                    reset_code.mark_as_used()

                    messages.success(request, 'Contraseña actualizada exitosamente. Ahora puedes iniciar sesión.')
                    return redirect('login:admin_login')
                    
                except AdminCredentials.DoesNotExist:
                    messages.error(request, 'No se encontraron credenciales para este email.')
                except Exception as e:
                    logger.error(f"Error al actualizar la contraseña tras recuperación: {e}", exc_info=True)
                    messages.error(request, 'No se pudo actualizar la contraseña. Intenta nuevamente.')
            else:
                messages.error(request, 'Código de verificación incorrecto.')
    else:
        form = PasswordResetVerifyForm()
    
    context = {
        'form': form,
        'email': email,
        'expires_at': reset_code.expires_at
    }
    
    return render(request, 'login/password_reset_verify.html', context)


def send_password_reset_email(email, code):
    """Envía email con código de recuperación"""
    subject = 'Recuperación de Contraseña - Tienda Inmobiliaria'
    
    # Crear el contenido del email
    html_content = render_to_string('login/emails/password_reset.html', {
        'email': email,
        'code': code,
        'site_name': 'Tienda Inmobiliaria'
    })
    
    text_content = f"""
    Recuperación de Contraseña - Tienda Inmobiliaria
    
    Hola,
    
    Has solicitado recuperar tu contraseña de administrador.
    
    Tu código de verificación es: {code}
    
    Este código expira en 1 hora.
    
    Si no solicitaste este cambio, ignora este email.
    
    Saludos,
    Equipo de Tienda Inmobiliaria
    """
    
    try:
        send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Error enviando email de recuperación de contraseña: {e}", exc_info=True)
        return False
