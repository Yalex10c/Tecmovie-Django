from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Usuario

def login_view(request):
    context = {}
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'login':
            correo = request.POST.get('correo')
            contrasena = request.POST.get('contrasena')
            
            user = Usuario.objects.filter(email=correo).first()
            if not user:
                user = Usuario.objects.filter(username=correo).first()
                
            if user and user.check_password(contrasena):
                login(request, user)
                return redirect('movies:home')
            else:
                context['error_login'] = "Correo o contraseña incorrectos."
                context['show_login_modal'] = True
                
        elif action == 'register':
            nombre = request.POST.get('nombre')
            correo = request.POST.get('correo')
            contrasena = request.POST.get('contrasena')
            
            if Usuario.objects.filter(email=correo).exists() or Usuario.objects.filter(username=correo).exists():
                context['error_register'] = "El correo ya está registrado."
                context['show_register_modal'] = True
            else:
                user = Usuario.objects.create_user(
                    username=correo,
                    email=correo,
                    password=contrasena,
                    first_name=nombre
                )
                from .models import Plan, Suscripcion
                from django.utils import timezone
                from datetime import timedelta
                plan_gratuito, _ = Plan.objects.get_or_create(nombre='Gratuita', defaults={'precio': 0.0, 'duracion_meses': 1})
                Suscripcion.objects.create(
                    usuario=user,
                    plan=plan_gratuito,
                    fecha_inicio=timezone.now().date(),
                    fecha_fin=timezone.now().date() + timedelta(days=30)
                )
                login(request, user)
                return redirect('movies:home')
                
    return render(request, 'index.htm', context)

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

def logout_view(request):
    logout(request)
    return redirect('users:login')

@login_required
def planes_view(request):
    from .models import Plan, Suscripcion
    from django.utils import timezone
    from datetime import timedelta

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'upgrade':
            plan_id = request.POST.get('plan_id')
            try:
                nuevo_plan = Plan.objects.get(id_plan=plan_id)
                # Borramos todas las suscripciones actuales para evitar conflictos
                request.user.suscripcion_set.all().delete()
                # Creamos la nueva suscripcion
                Suscripcion.objects.create(
                    usuario=request.user,
                    plan=nuevo_plan,
                    fecha_inicio=timezone.now().date(),
                    fecha_fin=timezone.now().date() + timedelta(days=nuevo_plan.duracion_meses * 30)
                )
                return redirect('users:planes')
            except Plan.DoesNotExist:
                pass

    planes_premium = Plan.objects.filter(precio__gt=0).order_by('precio')
    if not planes_premium.exists():
        Plan.objects.get_or_create(nombre='Plan Básico', defaults={'precio': 79.0, 'duracion_meses': 1})
        Plan.objects.get_or_create(nombre='Plan Premium', defaults={'precio': 99.0, 'duracion_meses': 1})
        Plan.objects.get_or_create(nombre='Plan Premium Plus', defaults={'precio': 129.0, 'duracion_meses': 1})
        planes_premium = Plan.objects.filter(precio__gt=0).order_by('precio')

    return render(request, 'planes.html', {'planes': planes_premium})
