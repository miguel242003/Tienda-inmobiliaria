from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from propiedades.models import Propiedad
from propiedades.forms import PropiedadForm
from django.http import JsonResponse
from .models import AdminCredentials
from .forms import AdminCredentialsForm, NuevoUsuarioAdminForm
from django.contrib.auth.hashers import check_password

def configurar_admin(request):
    """Vista para configurar credenciales del administrador (solo primera vez)"""
    # Verificar si ya existen credenciales
    if AdminCredentials.objects.filter(activo=True).exists():
        messages.warning(request, 'Las credenciales del administrador ya están configuradas.')
        return redirect('login:admin_login')
    
    if request.method == 'POST':
        form = AdminCredentialsForm(request.POST, request.FILES)
        if form.is_valid():
            # Guardar credenciales
            credenciales = form.save()
            
            # Crear usuario administrador
            try:
                user = User.objects.create_user(
                    username=credenciales.email,
                    email=credenciales.email,
                    password=form.cleaned_data['password'],
                    first_name=credenciales.nombre or 'Administrador',
                    last_name=credenciales.apellido or '',
                    is_staff=True,
                    is_superuser=True
                )
                
                messages.success(request, f'¡Administrador configurado exitosamente! Ahora puedes acceder con {credenciales.email}')
                return redirect('login:admin_login')
                
            except Exception as e:
                credenciales.delete()
                messages.error(request, f'Error al crear usuario: {str(e)}')
    else:
        form = AdminCredentialsForm()
    
    context = {
        'form': form,
        'es_configuracion_inicial': True,
    }
    return render(request, 'login/configurar_admin.html', context)

def admin_login(request):
    """Vista de login para administradores con credenciales seguras"""
    # Si el usuario ya está autenticado, redirigir al dashboard
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('login:dashboard')
    
    # Verificar si existen credenciales configuradas
    if not AdminCredentials.objects.filter(activo=True).exists():
        messages.info(request, 'Primera vez: Necesitas configurar las credenciales del administrador.')
        return redirect('login:configurar_admin')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            # Buscar credenciales
            credenciales = AdminCredentials.objects.get(email=email, activo=True)
            
            # Verificar contraseña
            if check_password(password, credenciales.password):
                # Buscar o crear usuario
                try:
                    user = User.objects.get(username=email)
                except User.DoesNotExist:
                    # Crear usuario si no existe
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        first_name=credenciales.nombre or 'Administrador',
                        last_name=credenciales.apellido or '',
                        is_staff=True,
                        is_superuser=True
                    )
                
                # Autenticar al usuario
                login(request, user)
                nombre_completo = credenciales.get_nombre_completo()
                messages.success(request, f'¡Bienvenido, {nombre_completo}!')
                return redirect('login:dashboard')
            else:
                messages.error(request, 'Correo o contraseña incorrectos.')
                
        except AdminCredentials.DoesNotExist:
            messages.error(request, 'Correo o contraseña incorrectos.')
        except Exception as e:
            messages.error(request, f'Error en el sistema: {str(e)}')
    
    return render(request, 'login/admin_login.html')

@login_required
def dashboard(request):
    """Dashboard del administrador"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('core:home')
    
    # Obtener estadísticas básicas
    total_users = User.objects.count()
    staff_users = User.objects.filter(is_staff=True).count()
    total_propiedades = Propiedad.objects.count()
    
    # Obtener propiedades recientes
    propiedades_recientes = Propiedad.objects.all().order_by('-fecha_creacion')[:5]
    
    # Obtener todas las propiedades para el selector del gráfico
    todas_propiedades = Propiedad.objects.all().order_by('titulo')
    
    # Importar el formulario para el modal
    from propiedades.forms import PropiedadForm
    form = PropiedadForm()
    
    # Obtener estadísticas de clics
    from propiedades.models import ClickPropiedad
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # Total de clics
    total_clicks = ClickPropiedad.objects.count()
    
    # Clics por mes (año actual completo: enero a diciembre)
    now = timezone.now()
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
            fecha_click__lt=fecha_fin
        ).count()
        
        clicks_por_mes.append({
            'mes': meses_nombres[mes - 1],
            'clicks': clicks_mes
        })
    
    # Clics por propiedad
    clicks_por_propiedad = {}
    for propiedad in todas_propiedades:
        # Obtener clics por mes para el año actual
        clicks_por_mes_propiedad = []
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
                propiedad=propiedad,
                fecha_click__gte=fecha_inicio,
                fecha_click__lt=fecha_fin
            ).count()
            
            clicks_por_mes_propiedad.append(clicks_mes)
        
        # Calcular total de clics para esta propiedad específica
        total_clicks_propiedad = sum(clicks_por_mes_propiedad)
        
        clicks_por_propiedad[propiedad.id] = {
            'clicks_totales': total_clicks_propiedad,
            'clicks_por_mes': clicks_por_mes_propiedad
        }
        
        # Debug: imprimir datos de cada propiedad
        print(f"Propiedad {propiedad.id} ({propiedad.titulo}): Total={total_clicks_propiedad}, Por mes={clicks_por_mes_propiedad}")
    
    # Debug: imprimir todos los datos generados
    print("=== DATOS FINALES GENERADOS ===")
    for prop_id, datos in clicks_por_propiedad.items():
        print(f"Propiedad {prop_id}: Total={datos['clicks_totales']}, Por mes={datos['clicks_por_mes']}")
    
    # Convertir clicks_por_propiedad a JSON para el template
    import json
    clicks_por_propiedad_json = json.dumps(clicks_por_propiedad)
    
    context = {
        'total_users': total_users,
        'staff_users': staff_users,
        'total_propiedades': total_propiedades,
        'propiedades_recientes': propiedades_recientes,
        'todas_propiedades': todas_propiedades,
        'total_clicks': total_clicks,
        'clicks_por_mes': clicks_por_mes,
        'clicks_por_propiedad': clicks_por_propiedad_json,
        'form': form,
    }
    
    return render(request, 'login/dashboard.html', context)

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

@login_required
def editar_propiedad(request, propiedad_id):
    """Vista para editar una propiedad existente"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para editar propiedades.')
        return redirect('core:home')
    
    propiedad = get_object_or_404(Propiedad, id=propiedad_id)
    
    if request.method == 'POST':
        form = PropiedadForm(request.POST, request.FILES, instance=propiedad)
        if form.is_valid():
            form.save()
            messages.success(request, f'Propiedad "{propiedad.titulo}" actualizada exitosamente.')
            return redirect('login:gestionar_propiedades')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = PropiedadForm(instance=propiedad)
    
    context = {
        'form': form,
        'propiedad': propiedad,
        'titulo_pagina': 'Editar Propiedad',
    }
    return render(request, 'login/editar_propiedad.html', context)

@login_required
def eliminar_propiedad(request, propiedad_id):
    """Vista para eliminar una propiedad"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para eliminar propiedades.')
        return redirect('core:home')
    
    propiedad = get_object_or_404(Propiedad, id=propiedad_id)
    
    if request.method == 'POST':
        titulo = propiedad.titulo
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
            propiedad.delete()
            return JsonResponse({
                'success': True, 
                'message': f'Propiedad "{titulo}" eliminada exitosamente.',
                'propiedad_id': propiedad_id
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al eliminar: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

@login_required
def actualizar_perfil(request):
    """Vista AJAX para actualizar el perfil del administrador"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'No tienes permisos para actualizar el perfil.'})
    
    if request.method == 'POST':
        try:
            # Buscar o crear AdminCredentials
            from .models import AdminCredentials
            try:
                admin_creds = AdminCredentials.objects.get(email=request.user.email)
            except AdminCredentials.DoesNotExist:
                admin_creds = AdminCredentials.objects.create(
                    nombre=request.user.first_name or 'Administrador',
                    apellido=request.user.last_name or 'del Sistema',
                    email=request.user.email,
                    telefono='+52-1-33-00000000',
                    password='temp_password_123'
                )
            
            # Actualizar campos
            admin_creds.nombre = request.POST.get('nombre', admin_creds.nombre)
            admin_creds.apellido = request.POST.get('apellido', admin_creds.apellido)
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
            return JsonResponse({'success': False, 'message': f'Error al actualizar el perfil: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

@login_required
def crear_nuevo_usuario_admin(request):
    """Vista AJAX para crear un nuevo usuario administrativo"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'No tienes permisos para crear usuarios administrativos.'})
    
    if request.method == 'POST':
        try:
            form = NuevoUsuarioAdminForm(request.POST, request.FILES)
            if form.is_valid():
                # Guardar credenciales
                credenciales = form.save()
                
                # Crear usuario administrador
                try:
                    user = User.objects.create_user(
                        username=credenciales.email,
                        email=credenciales.email,
                        password=form.cleaned_data['password'],
                        first_name=credenciales.nombre or 'Administrador',
                        last_name=credenciales.apellido or '',
                        is_staff=True,
                        is_superuser=True
                    )
                    
                    return JsonResponse({
                        'success': True, 
                        'message': f'Usuario administrativo "{credenciales.get_nombre_completo()}" creado exitosamente.',
                        'usuario': {
                            'nombre': credenciales.get_nombre_completo(),
                            'email': credenciales.email,
                            'fecha_creacion': credenciales.fecha_creacion.strftime('%d/%m/%Y %H:%M')
                        }
                    })
                    
                except Exception as e:
                    credenciales.delete()
                    return JsonResponse({'success': False, 'message': f'Error al crear usuario: {str(e)}'})
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
            return JsonResponse({'success': False, 'message': f'Error al procesar la solicitud: {str(e)}'})
    
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
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
