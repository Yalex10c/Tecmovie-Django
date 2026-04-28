from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q, F, IntegerField, ExpressionWrapper
from django.shortcuts import render, get_object_or_404, redirect

from django.utils import timezone
from apps.interactions.models import HistorialVisita
from .models import Pelicula, Genero, Actor, Director
from apps.reviews.models import Resena, Calificacion


def home_top_peliculas(request):
    query = request.GET.get('q', '').strip()
    genero_id = request.GET.get('genero', '').strip()

    peliculas = (
        Pelicula.objects
        .prefetch_related('generos', 'directores')
        .annotate(
            total_likes=Count('calificacion', filter=Q(calificacion__reaccion='like')),
            total_dislikes=Count('calificacion', filter=Q(calificacion__reaccion='dislike'))
        )
        .all()
    )

    if query:
        peliculas = peliculas.filter(
            Q(nombre__icontains=query) |
            Q(generos__nombre__icontains=query) |
            Q(directores__nombre__icontains=query)
        ).distinct()

    if genero_id:
        peliculas = peliculas.filter(generos__id_genero=genero_id).distinct()

    peliculas = peliculas.order_by('nombre')

    paginator = Paginator(peliculas, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    top_peliculas = (
        Pelicula.objects
        .prefetch_related('generos', 'directores')
        .annotate(
            total_likes=Count('calificacion', filter=Q(calificacion__reaccion='like')),
            total_dislikes=Count('calificacion', filter=Q(calificacion__reaccion='dislike'))
        )
        .order_by('-total_likes', 'total_dislikes', 'nombre')
        .distinct()[:10]
    )

    generos = Genero.objects.all().order_by('nombre')

    context = {
        'page_obj': page_obj,
        'top_peliculas': top_peliculas,
        'generos': generos,
        'query': query,
        'genero_id': genero_id,
    }
    return render(request, 'index2.html', context)


def nuevas_peliculas(request):
    peliculas = (
        Pelicula.objects
        .prefetch_related('generos', 'directores')
        .annotate(
            promedio_calificacion=Avg('calificacion'),
            total_calificaciones=Count('calificacion')
        )
        .order_by('-anio', 'nombre')
    )

    paginator = Paginator(peliculas, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'index4.html', {'page_obj': page_obj})


def detalle_pelicula(request, id):
    pelicula = get_object_or_404(
        Pelicula.objects.prefetch_related('generos', 'directores', 'actores', 'plataformas'),
        pk=id
    )

    if request.user.is_authenticated:
        hace_24_horas = timezone.now() - timezone.timedelta(hours=24)

        visita_reciente = HistorialVisita.objects.filter(
            usuario=request.user,
            pelicula=pelicula,
            fecha_visita__gte=hace_24_horas
        ).exists()

        if not visita_reciente:
            HistorialVisita.objects.create(
                usuario=request.user,
                pelicula=pelicula,
                fecha_visita=timezone.now()
            )

    if request.method == 'POST' and request.user.is_authenticated and request.user.can_interact:
        comentario = request.POST.get('comentario')
        if comentario:
            Resena.objects.create(
                pelicula=pelicula,
                usuario=request.user,
                comentario=comentario
            )
            return redirect('movies:detalle', id=id)

    is_favorite = False
    is_in_watchlist = False
    can_interact = False
    user_reaction = None

    total_likes = Calificacion.objects.filter(
        pelicula=pelicula,
        reaccion='like'
    ).count()

    total_dislikes = Calificacion.objects.filter(
        pelicula=pelicula,
        reaccion='dislike'
    ).count()

    if request.user.is_authenticated:
        from apps.interactions.models import Favorite, Watchlist

        is_favorite = Favorite.objects.filter(user=request.user, movie=pelicula).exists()
        is_in_watchlist = Watchlist.objects.filter(user=request.user, movie=pelicula).exists()
        can_interact = request.user.can_interact

        user_reaction_obj = Calificacion.objects.filter(
            usuario=request.user,
            pelicula=pelicula
        ).first()

        if user_reaction_obj:
            user_reaction = user_reaction_obj.reaccion

    resenas = (
        Resena.objects
        .filter(pelicula=pelicula)
        .select_related('usuario')
        .order_by('-fecha')
    )
    

    context = {
        'pelicula': pelicula,
        'resenas': resenas,
        'is_favorite': is_favorite,
        'is_in_watchlist': is_in_watchlist,
        'can_interact': can_interact,
        'user_reaction': user_reaction,
        'total_likes': total_likes,
        'total_dislikes': total_dislikes,
    }

    return render(request, 'index3.html', context)

def lista_actores(request):
    query = request.GET.get('q', '').strip()

    actores = (
        Actor.objects
        .annotate(
            total_peliculas=Count('peliculas', distinct=True),
            likes_acumulados=Count(
                'peliculas__calificacion',
                filter=Q(peliculas__calificacion__reaccion='like'),
                distinct=True
            ),
            dislikes_acumulados=Count(
                'peliculas__calificacion',
                filter=Q(peliculas__calificacion__reaccion='dislike'),
                distinct=True
            )
        )
        .order_by('-likes_acumulados', '-total_peliculas', 'nombre')
    )

    if query:
        actores = actores.filter(
            Q(nombre__icontains=query) |
            Q(pais_origen__icontains=query) |
            Q(biografia__icontains=query)
        )

    paginator = Paginator(actores, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for actor in page_obj:
        total_reacciones = actor.likes_acumulados + actor.dislikes_acumulados
        actor.porcentaje_positivo = round((actor.likes_acumulados * 100) / total_reacciones, 1) if total_reacciones > 0 else None

    return render(request, 'actores.html', {
        'page_obj': page_obj,
        'query': query,
    })


def detalle_actor(request, id):
    actor = get_object_or_404(
        Actor.objects.annotate(
            total_peliculas=Count('peliculas', distinct=True),
            likes_acumulados=Count(
                'peliculas__calificacion',
                filter=Q(peliculas__calificacion__reaccion='like'),
                distinct=True
            ),
            dislikes_acumulados=Count(
                'peliculas__calificacion',
                filter=Q(peliculas__calificacion__reaccion='dislike'),
                distinct=True
            )
        ),
        pk=id
    )

    peliculas_actor = (
        actor.peliculas
        .prefetch_related('generos', 'directores')
        .annotate(
            total_likes=Count('calificacion', filter=Q(calificacion__reaccion='like')),
            total_dislikes=Count('calificacion', filter=Q(calificacion__reaccion='dislike'))
        )
        .order_by('-anio', 'nombre')
        .distinct()
    )

    total_reacciones = actor.likes_acumulados + actor.dislikes_acumulados
    porcentaje_positivo = round((actor.likes_acumulados * 100) / total_reacciones, 1) if total_reacciones > 0 else None

    context = {
        'actor': actor,
        'peliculas_actor': peliculas_actor,
        'porcentaje_positivo': porcentaje_positivo,
    }

    return render(request, 'detalle_actor.html', context)

def tendencias_peliculas(request):
    ahora = timezone.now()
    hace_7_dias = ahora - timezone.timedelta(days=7)

    recien_llegadas = (
        Pelicula.objects
        .prefetch_related('generos', 'directores')
        .annotate(
            total_likes=Count('calificacion', filter=Q(calificacion__reaccion='like')),
            total_dislikes=Count('calificacion', filter=Q(calificacion__reaccion='dislike'))
        )
        .order_by('-id_pelicula')[:12]
    )

    mas_visitadas_semana = (
    Pelicula.objects
    .prefetch_related('generos', 'directores')
    .annotate(
        visitas_semana=Count(
            'visitas_usuario',
            filter=Q(visitas_usuario__fecha_visita__gte=hace_7_dias),
            distinct=True
        ),
        total_likes=Count(
            'calificacion',
            filter=Q(calificacion__reaccion='like'),
            distinct=True
        ),
        total_dislikes=Count(
            'calificacion',
            filter=Q(calificacion__reaccion='dislike'),
            distinct=True
        )
    )
    .filter(visitas_semana__gt=0)
    .annotate(
        puntaje_tendencia=ExpressionWrapper(
            F('visitas_semana') * 3 + F('total_likes') * 2 - F('total_dislikes'),
            output_field=IntegerField()
        )
    )
    .order_by('-puntaje_tendencia', '-visitas_semana', '-total_likes', 'total_dislikes', 'nombre')[:12]
)

    principal_tendencia = mas_visitadas_semana[0] if mas_visitadas_semana else None

    context = {
        'recien_llegadas': recien_llegadas,
        'mas_visitadas_semana': mas_visitadas_semana,
        'principal_tendencia': principal_tendencia,       
    }

    return render(request, 'index_tendencias.html', context)

def lista_directores(request):
    query = request.GET.get('q', '').strip()

    directores = (
        Director.objects
        .annotate(
            total_peliculas=Count('peliculas', distinct=True),
            likes_acumulados=Count(
                'peliculas__calificacion',
                filter=Q(peliculas__calificacion__reaccion='like'),
                distinct=True
            ),
            dislikes_acumulados=Count(
                'peliculas__calificacion',
                filter=Q(peliculas__calificacion__reaccion='dislike'),
                distinct=True
            )
        )
        .order_by('-likes_acumulados', '-total_peliculas', 'nombre')
    )

    if query:
        directores = directores.filter(
            Q(nombre__icontains=query) |
            Q(pais_origen__icontains=query) |
            Q(biografia__icontains=query) |
            Q(conocido_por__icontains=query)
        )

    paginator = Paginator(directores, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for director in page_obj:
        total_reacciones = director.likes_acumulados + director.dislikes_acumulados
        director.porcentaje_positivo = round((director.likes_acumulados * 100) / total_reacciones, 1) if total_reacciones > 0 else None

    return render(request, 'directores.html', {
        'page_obj': page_obj,
        'query': query,
    })

def detalle_director(request, id):
    director = get_object_or_404(
        Director.objects.annotate(
            total_peliculas=Count('peliculas', distinct=True),
            likes_acumulados=Count(
                'peliculas__calificacion',
                filter=Q(peliculas__calificacion__reaccion='like'),
                distinct=True
            ),
            dislikes_acumulados=Count(
                'peliculas__calificacion',
                filter=Q(peliculas__calificacion__reaccion='dislike'),
                distinct=True
            )
        ),
        pk=id
    )

    peliculas_director = (
        director.peliculas
        .prefetch_related('generos')
        .annotate(
            total_likes=Count('calificacion', filter=Q(calificacion__reaccion='like')),
            total_dislikes=Count('calificacion', filter=Q(calificacion__reaccion='dislike'))
        )
        .order_by('-anio', 'nombre')
        .distinct()
    )

    total_reacciones = director.likes_acumulados + director.dislikes_acumulados
    porcentaje_positivo = round((director.likes_acumulados * 100) / total_reacciones, 1) if total_reacciones > 0 else None

    context = {
        'director': director,
        'peliculas_director': peliculas_director,
        'porcentaje_positivo': porcentaje_positivo,
    }

    return render(request, 'detalle_director.html', context)

