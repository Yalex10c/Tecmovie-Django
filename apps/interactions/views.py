from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Favorite, Watchlist
from apps.movies.models import Pelicula
from apps.reviews.models import Calificacion
from django.http import HttpResponseRedirect
from django.urls import reverse

@login_required
def toggle_favorite(request, movie_id):
    if request.user.can_interact:
        movie = get_object_or_404(Pelicula, pk=movie_id)
        fav, created = Favorite.objects.get_or_create(user=request.user, movie=movie)
        if not created:
            fav.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('movies:detalle', args=[movie_id])))

@login_required
def toggle_watchlist(request, movie_id):
    if request.user.can_interact:
        movie = get_object_or_404(Pelicula, pk=movie_id)
        watch, created = Watchlist.objects.get_or_create(user=request.user, movie=movie)
        if not created:
            watch.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('movies:detalle', args=[movie_id])))

@login_required
def rate_movie(request, movie_id):
    if request.method == 'POST' and request.user.can_interact:
        movie = get_object_or_404(Pelicula, pk=movie_id)
        reaccion = request.POST.get('reaccion')

        if reaccion in ['like', 'dislike']:
            calificacion, created = Calificacion.objects.get_or_create(
                usuario=request.user,
                pelicula=movie,
                defaults={'reaccion': reaccion}
            )

            if not created:
                if calificacion.reaccion == reaccion:
                    calificacion.delete()
                else:
                    calificacion.reaccion = reaccion
                    calificacion.save()

    return HttpResponseRedirect(
        request.META.get('HTTP_REFERER', reverse('movies:detalle', args=[movie_id]))
    )
