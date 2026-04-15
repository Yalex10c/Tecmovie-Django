from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.shortcuts import render, get_object_or_404, redirect

from .models import Pelicula, Genero
from apps.reviews.models import Resena, Calificacion


def home_top_peliculas(request):
    query = request.GET.get('q', '').strip()
    genero_id = request.GET.get('genero', '').strip()

    peliculas = (
        Pelicula.objects
        .prefetch_related('generos', 'directores')
        .annotate(
            promedio_calificacion=Avg('calificacion__puntuacion'),
            total_calificaciones=Count('calificacion')
        )
    )

    if query:
        peliculas = peliculas.filter(
            Q(nombre__icontains=query) |
            Q(genero__nombre__icontains=query) |
            Q(director__nombre__icontains=query)
        )

    if genero_id:
        peliculas = peliculas.filter(genero_id=genero_id)

    peliculas = peliculas.order_by('-anio', 'nombre')

    paginator = Paginator(peliculas, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    top_peliculas = (
        Pelicula.objects
        .select_related('genero')
        .annotate(
            promedio_calificacion=Avg('calificacion__puntuacion'),
            total_calificaciones=Count('calificacion')
        )
        .order_by('-promedio_calificacion', '-total_calificaciones', 'nombre')[:10]
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
        .distinct()
    )

    paginator = Paginator(peliculas, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'index4.html', {'page_obj': page_obj})

def detalle_pelicula(request, id):
    pelicula = get_object_or_404(
        Pelicula.objects.select_related('genero', 'director'),
        pk=id
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

    context = {
        'pelicula': pelicula,
        'resenas': resenas,
        'is_favorite': is_favorite,
        'is_in_watchlist': is_in_watchlist,
        'can_interact': can_interact,
        'user_rating': user_rating,
        'promedio_calificacion': promedio_calificacion,
    }
    return render(request, 'index3.html', context)