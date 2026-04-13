from django.shortcuts import render, get_object_or_404, redirect
from .models import Pelicula
from apps.reviews.models import Resena

def home_top_peliculas(request):
    movies = Pelicula.objects.select_related('genero').all()[:5]
    context = {'movies': movies}
    return render(request, 'index2.html', context)

def nuevas_peliculas(request):
    return render(request, 'index4.html')

def detalle_pelicula(request, id):
    pelicula = get_object_or_404(Pelicula.objects.select_related('genero', 'director'), pk=id)
    
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
    if request.user.is_authenticated:
        from apps.interactions.models import Favorite, Watchlist
        is_favorite = Favorite.objects.filter(user=request.user, movie=pelicula).exists()
        is_in_watchlist = Watchlist.objects.filter(user=request.user, movie=pelicula).exists()
        can_interact = request.user.can_interact

    resenas = Resena.objects.filter(pelicula=pelicula).select_related('usuario').order_by('-fecha')
    
    context = {
        'pelicula': pelicula,
        'resenas': resenas,
        'is_favorite': is_favorite,
        'is_in_watchlist': is_in_watchlist,
        'can_interact': can_interact
    }
    return render(request, 'index3.html', context)
