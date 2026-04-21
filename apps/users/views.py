from datetime import timedelta

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Avg, Count, Q
from apps.reviews.models import Calificacion

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

from .forms import LoginForm, RegisterForm, MiMundoForm
from .models import Usuario, Plan, Suscripcion, UsuarioGeneroPreferencia
from apps.movies.models import Genero, Pelicula
from collections import Counter
from apps.interactions.models import Favorite, Watchlist, HistorialVisita


def login_view(request):
    context = {
        'login_form': LoginForm(),
        'register_form': RegisterForm(),
    }

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'login':
            form = LoginForm(request.POST)
            context['login_form'] = form

            if form.is_valid():
                user = form.cleaned_data['user']
                login(request, user)
                return redirect('movies:home')

            context['error_login'] = form.errors.get('__all__', ['Error al iniciar sesión'])[0]
            context['show_login_modal'] = True

        elif action == 'register':
            form = RegisterForm(request.POST)
            context['register_form'] = form

            if form.is_valid():
                nombre = form.cleaned_data['nombre']
                correo = form.cleaned_data['correo']
                contrasena = form.cleaned_data['contrasena']

                user = Usuario.objects.create_user(
                    username=correo,
                    email=correo,
                    password=contrasena,
                    first_name=nombre
                )

                plan_gratuito, _ = Plan.objects.get_or_create(
                    nombre='Gratuita',
                    defaults={'precio': 0.0, 'duracion_meses': 1}
                )

                Suscripcion.objects.create(
                    usuario=user,
                    plan=plan_gratuito,
                    fecha_inicio=timezone.now().date(),
                    fecha_fin=timezone.now().date() + timedelta(days=30)
                )

                authenticated_user = authenticate(username=correo, password=contrasena)
                if authenticated_user:
                    login(request, authenticated_user)

                return redirect('movies:home')

            if form.errors:
                errores = []
                for field, error_list in form.errors.items():
                    for error in error_list:
                        errores.append(f"{field}: {error}")
                context['error_register'] = " | ".join(errores)
            else:
                context['error_register'] = "Error en el registro"

            context['show_register_modal'] = True

    return render(request, 'index.htm', context)


def logout_view(request):
    logout(request)
    return redirect('users:login')


@login_required
def planes_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'upgrade':
            plan_id = request.POST.get('plan_id')
            try:
                nuevo_plan = Plan.objects.get(id_plan=plan_id)

                request.user.suscripcion_set.all().delete()

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

@login_required
def mi_mundo_view(request):
    preferencias_actuales = UsuarioGeneroPreferencia.objects.filter(
        usuario=request.user
    ).values_list('genero_id', flat=True)

    if request.method == 'POST':
        form = MiMundoForm(request.POST)

        if form.is_valid():
            generos_seleccionados = form.cleaned_data['generos']

            UsuarioGeneroPreferencia.objects.filter(usuario=request.user).delete()

            for genero in generos_seleccionados:
                UsuarioGeneroPreferencia.objects.create(
                    usuario=request.user,
                    genero=genero
                )

            return redirect('users:mi_mundo')
    else:
        form = MiMundoForm(initial={
            'generos': list(preferencias_actuales)
        })

    generos_elegidos = Genero.objects.filter(
        id_genero__in=preferencias_actuales
    ).order_by('nombre')

    peliculas_calificadas_ids = list(
        Calificacion.objects.filter(usuario=request.user).values_list('pelicula_id', flat=True)
    )

    favoritos_ids = list(
        Favorite.objects.filter(user=request.user).values_list('movie_id', flat=True)
    )

    watchlist_ids = list(
        Watchlist.objects.filter(user=request.user).values_list('movie_id', flat=True)
    )

    visitas_ids = list(
        HistorialVisita.objects.filter(usuario=request.user)
        .order_by('-fecha_visita')
        .values_list('pelicula_id', flat=True)
    )

    genero_scores = Counter()

    for genero_id in preferencias_actuales:
        genero_scores[genero_id] += 4

    peliculas_favoritas = Pelicula.objects.filter(id_pelicula__in=favoritos_ids).prefetch_related('generos')
    for pelicula in peliculas_favoritas:
        for genero in pelicula.generos.all():
            genero_scores[genero.id_genero] += 3

    peliculas_watchlist = Pelicula.objects.filter(id_pelicula__in=watchlist_ids).prefetch_related('generos')
    for pelicula in peliculas_watchlist:
        for genero in pelicula.generos.all():
            genero_scores[genero.id_genero] += 2

    peliculas_visitadas = Pelicula.objects.filter(id_pelicula__in=visitas_ids).prefetch_related('generos')
    for pelicula in peliculas_visitadas:
        for genero in pelicula.generos.all():
            genero_scores[genero.id_genero] += 1

    genero_ids_relevantes = list(genero_scores.keys())

    recomendaciones = []
    if genero_ids_relevantes:
        recomendaciones = (
            Pelicula.objects
            .prefetch_related('generos', 'directores')
            .annotate(
                promedio_calificacion=Avg('calificaciones__puntuacion'),
                total_calificaciones=Count('calificaciones'),
                coincidencias_genero=Count(
                    'generos',
                    filter=Q(generos__id_genero__in=genero_ids_relevantes),
                    distinct=True
                )
            )
            .filter(generos__id_genero__in=genero_ids_relevantes)
            .exclude(id_pelicula__in=peliculas_calificadas_ids)
            .distinct()
            .order_by('-coincidencias_genero', '-promedio_calificacion', 'nombre')[:6]
        )

    favoritas = (
        Favorite.objects
        .filter(user=request.user)
        .select_related('movie')
        .prefetch_related('movie__generos')
        .order_by('-created_at')[:6]
    )

    watchlist = (
        Watchlist.objects
        .filter(user=request.user)
        .select_related('movie')
        .prefetch_related('movie__generos')
        .order_by('-created_at')[:6]
    )

    vistas_recientes_ids = []
    for pelicula_id in visitas_ids:
        if pelicula_id not in vistas_recientes_ids:
            vistas_recientes_ids.append(pelicula_id)

    vistas_recientes_ids = vistas_recientes_ids[:6]

    peliculas_recientes_map = {
        pelicula.id_pelicula: pelicula
        for pelicula in Pelicula.objects.filter(id_pelicula__in=vistas_recientes_ids).prefetch_related('generos')
    }

    vistas_recientes = [
        peliculas_recientes_map[pelicula_id]
        for pelicula_id in vistas_recientes_ids
        if pelicula_id in peliculas_recientes_map
    ]

    return render(request, 'mi_mundo.html', {
        'form': form,
        'generos_elegidos': generos_elegidos,
        'recomendaciones': recomendaciones,
        'favoritas': favoritas,
        'watchlist': watchlist,
        'vistas_recientes': vistas_recientes,
    })

@login_required
def recomendaciones_view(request):
    preferencias_actuales = list(
        UsuarioGeneroPreferencia.objects.filter(
            usuario=request.user
        ).values_list('genero_id', flat=True)
    )

    peliculas_calificadas_ids = list(
        Calificacion.objects.filter(usuario=request.user).values_list('pelicula_id', flat=True)
    )

    favoritos_ids = list(
        Favorite.objects.filter(user=request.user).values_list('movie_id', flat=True)
    )

    watchlist_ids = list(
        Watchlist.objects.filter(user=request.user).values_list('movie_id', flat=True)
    )

    visitas_ids = list(
        HistorialVisita.objects.filter(usuario=request.user)
        .order_by('-fecha_visita')
        .values_list('pelicula_id', flat=True)
    )

    genero_scores = Counter()

    for genero_id in preferencias_actuales:
        genero_scores[genero_id] += 4

    peliculas_favoritas = Pelicula.objects.filter(
        id_pelicula__in=favoritos_ids
    ).prefetch_related('generos')
    for pelicula in peliculas_favoritas:
        for genero in pelicula.generos.all():
            genero_scores[genero.id_genero] += 3

    peliculas_watchlist = Pelicula.objects.filter(
        id_pelicula__in=watchlist_ids
    ).prefetch_related('generos')
    for pelicula in peliculas_watchlist:
        for genero in pelicula.generos.all():
            genero_scores[genero.id_genero] += 2

    peliculas_visitadas = Pelicula.objects.filter(
        id_pelicula__in=visitas_ids
    ).prefetch_related('generos')
    for pelicula in peliculas_visitadas:
        for genero in pelicula.generos.all():
            genero_scores[genero.id_genero] += 1

    genero_ids_relevantes = list(genero_scores.keys())

    recomendaciones = []
    generos_relevantes = []

    if genero_ids_relevantes:
        recomendaciones = (
            Pelicula.objects
            .prefetch_related('generos', 'directores')
            .annotate(
                promedio_calificacion=Avg('calificaciones__puntuacion'),
                total_calificaciones=Count('calificaciones'),
                coincidencias_genero=Count(
                    'generos',
                    filter=Q(generos__id_genero__in=genero_ids_relevantes),
                    distinct=True
                )
            )
            .filter(generos__id_genero__in=genero_ids_relevantes)
            .exclude(id_pelicula__in=peliculas_calificadas_ids)
            .distinct()
            .order_by('-coincidencias_genero', '-promedio_calificacion', 'nombre')
        )

        generos_relevantes = Genero.objects.filter(
            id_genero__in=genero_ids_relevantes
        ).order_by('nombre')

    return render(request, 'recomendaciones.html', {
        'recomendaciones': recomendaciones,
        'generos_relevantes': generos_relevantes,
    })

@login_required
def cambiar_contrasena_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Tu contraseña se cambió correctamente.')
            return redirect('users:cambiar_contrasena')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'cambiar_contrasena.html', {
        'form': form
    })