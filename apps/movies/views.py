from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.shortcuts import render, get_object_or_404, redirect

from django.utils import timezone
from apps.interactions.models import HistorialVisita
from .models import Pelicula, Genero
from apps.reviews.models import Resena, Calificacion


def home_top_peliculas(request):
    query = request.GET.get('q', '').strip()
    genero_id = request.GET.get('genero', '').strip()

    peliculas = (
        Pelicula.objects
        .prefetch_related('generos', 'directores')
        .annotate(
            promedio_calificacion=Avg('calificaciones__puntuacion'),
            total_calificaciones=Count('calificaciones')
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
            promedio_calificacion=Avg('calificaciones__puntuacion'),
            total_calificaciones=Count('calificaciones')
        )
        .order_by('-promedio_calificacion', '-total_calificaciones', 'nombre')
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
            promedio_calificacion=Avg('calificaciones__puntuacion'),
            total_calificaciones=Count('calificaciones')
        )
        .order_by('-anio', 'nombre')
    )

    paginator = Paginator(peliculas, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'index4.html', {'page_obj': page_obj})


def detalle_pelicula(request, id):
    pelicula = get_object_or_404(
        Pelicula.objects.prefetch_related(
            'generos',
            'directores',
            'actores',
            'plataformas'
        ),
        pk=id
    )

    if request.user.is_authenticated:
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
    user_rating = None

    promedio_calificacion = (
        Calificacion.objects
        .filter(pelicula=pelicula)
        .aggregate(promedio=Avg('puntuacion'))
        .get('promedio')
    )

    if request.user.is_authenticated:
        from apps.interactions.models import Favorite, Watchlist

        is_favorite = Favorite.objects.filter(user=request.user, movie=pelicula).exists()
        is_in_watchlist = Watchlist.objects.filter(user=request.user, movie=pelicula).exists()
        can_interact = request.user.can_interact

        user_rating_obj = Calificacion.objects.filter(
            usuario=request.user,
            pelicula=pelicula
        ).first()

        if user_rating_obj:
            user_rating = user_rating_obj.puntuacion

    resenas = (
        Resena.objects
        .filter(pelicula=pelicula)
        .select_related('usuario')
        .order_by('-fecha')
    )

    selected_rating = ''
    if user_rating is not None:
        try:
            selected_rating = str(int(float(user_rating)))
        except (ValueError, TypeError):
            selected_rating = ''

    genero_ids = pelicula.generos.values_list('id_genero', flat=True)
    director_ids = pelicula.directores.values_list('id_director', flat=True)

    peliculas_similares = (
        Pelicula.objects
        .prefetch_related('generos', 'directores')
        .annotate(
            promedio_calificacion=Avg('calificaciones__puntuacion'),
            total_calificaciones=Count('calificaciones'),
            coincidencias_genero=Count(
                'generos',
                filter=Q(generos__id_genero__in=genero_ids),
                distinct=True
            ),
            coincidencias_director=Count(
                'directores',
                filter=Q(directores__id_director__in=director_ids),
                distinct=True
            ),
        )
        .exclude(id_pelicula=pelicula.id_pelicula)
        .filter(
            Q(generos__id_genero__in=genero_ids) |
            Q(directores__id_director__in=director_ids)
        )
        .distinct()
        .order_by(
            '-coincidencias_director',
            '-coincidencias_genero',
            '-promedio_calificacion',
            'nombre'
        )[:6]
    )

    context = {
        'pelicula': pelicula,
        'resenas': resenas,
        'is_favorite': is_favorite,
        'is_in_watchlist': is_in_watchlist,
        'can_interact': can_interact,
        'user_rating': user_rating,
        'selected_rating': selected_rating,
        'promedio_calificacion': promedio_calificacion,
        'peliculas_similares': peliculas_similares,
    }
    return render(request, 'index3.html', context)