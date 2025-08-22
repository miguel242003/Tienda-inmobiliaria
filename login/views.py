from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from propiedades.models import Propiedad
from propiedades.forms import PropiedadForm
from django.http import JsonResponse
from .models import AdminCredentials
from .forms import AdminCredentialsForm
from django.contrib.auth.hashers import check_password

def configurar_admin(request):
    """Vista para configurar credenciales del administrador (solo primera vez)"""
    # Verificar si ya existen credenciales
    if AdminCredentials.objects.filter(activo=True).exists():
        messages.warning(request, 'Las credenciales del administrador ya están configuradas.')
        return redirect('login:admin_login')
    
    if request.method == 'POST':
        form = AdminCredentialsForm(request.POST)
        if form.is_valid():
            # Guardar credenciales
            credenciales = form.save()
            
            # Crear usuario administrador
            try:
                user = User.objects.create_user(
                    username=credenciales.email,
                    email=credenciales.email,
                    password=form.cleaned_data['password'],
                    first_name='Administrador',
                    last_name='',
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
                        first_name='Administrador',
                        last_name='',
                        is_staff=True,
                        is_superuser=True
                    )
                
                # Autenticar al usuario
                login(request, user)
                messages.success(request, f'¡Bienvenido, {user.first_name}!')
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
    
    context = {
        'total_users': total_users,
        'staff_users': staff_users,
        'total_propiedades': total_propiedades,
        'propiedades_recientes': propiedades_recientes,
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
