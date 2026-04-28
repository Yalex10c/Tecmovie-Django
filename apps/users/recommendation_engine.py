from collections import Counter
from django.db.models import Count, Q

from apps.movies.models import Pelicula, Genero
from apps.reviews.models import Calificacion
from apps.interactions.models import Favorite, Watchlist, HistorialVisita
from apps.users.models import UsuarioGeneroPreferencia


def _sumar_peso_pelicula(
    pelicula,
    pesos_generos,
    pesos_directores,
    pesos_actores,
    pesos_plataformas,
    peso_genero,
    peso_director,
    peso_actor,
    peso_plataforma,
):
    for genero in pelicula.generos.all():
        pesos_generos[genero.id_genero] += peso_genero

    for director in pelicula.directores.all():
        pesos_directores[director.id_director] += peso_director

    for actor in pelicula.actores.all():
        pesos_actores[actor.id_actor] += peso_actor

    for plataforma in pelicula.plataformas.all():
        pesos_plataformas[plataforma.id_plataforma] += peso_plataforma


def obtener_recomendaciones_para_usuario(usuario, limite=12):
    preferencias_ids = list(
        UsuarioGeneroPreferencia.objects
        .filter(usuario=usuario)
        .values_list("genero_id", flat=True)
    )

    likes_ids = list(
        Calificacion.objects
        .filter(usuario=usuario, reaccion="like")
        .values_list("pelicula_id", flat=True)
    )

    dislikes_ids = list(
        Calificacion.objects
        .filter(usuario=usuario, reaccion="dislike")
        .values_list("pelicula_id", flat=True)
    )

    favoritos_ids = list(
        Favorite.objects
        .filter(user=usuario)
        .values_list("movie_id", flat=True)
    )

    watchlist_ids = list(
        Watchlist.objects
        .filter(user=usuario)
        .values_list("movie_id", flat=True)
    )

    visitas_ids = list(
        HistorialVisita.objects
        .filter(usuario=usuario)
        .order_by("-fecha_visita")
        .values_list("pelicula_id", flat=True)
    )

    pesos_generos = Counter()
    pesos_directores = Counter()
    pesos_actores = Counter()
    pesos_plataformas = Counter()

    generos_negativos = Counter()
    directores_negativos = Counter()
    actores_negativos = Counter()

    for genero_id in preferencias_ids:
        pesos_generos[genero_id] += 5

    peliculas_positivas = (
        Pelicula.objects
        .filter(id_pelicula__in=set(likes_ids + favoritos_ids + watchlist_ids))
        .prefetch_related("generos", "directores", "actores", "plataformas")
    )

    for pelicula in peliculas_positivas:
        if pelicula.id_pelicula in likes_ids:
            _sumar_peso_pelicula(
                pelicula,
                pesos_generos,
                pesos_directores,
                pesos_actores,
                pesos_plataformas,
                peso_genero=7,
                peso_director=12,
                peso_actor=10,
                peso_plataforma=3,
            )

        if pelicula.id_pelicula in favoritos_ids:
            _sumar_peso_pelicula(
                pelicula,
                pesos_generos,
                pesos_directores,
                pesos_actores,
                pesos_plataformas,
                peso_genero=6,
                peso_director=10,
                peso_actor=8,
                peso_plataforma=3,
            )

        if pelicula.id_pelicula in watchlist_ids:
            _sumar_peso_pelicula(
                pelicula,
                pesos_generos,
                pesos_directores,
                pesos_actores,
                pesos_plataformas,
                peso_genero=4,
                peso_director=6,
                peso_actor=5,
                peso_plataforma=2,
            )

    peliculas_visitadas = (
        Pelicula.objects
        .filter(id_pelicula__in=visitas_ids[:20])
        .prefetch_related("generos", "directores", "actores", "plataformas")
    )

    for pelicula in peliculas_visitadas:
        _sumar_peso_pelicula(
            pelicula,
            pesos_generos,
            pesos_directores,
            pesos_actores,
            pesos_plataformas,
            peso_genero=2,
            peso_director=3,
            peso_actor=3,
            peso_plataforma=1,
        )

    peliculas_dislike = (
        Pelicula.objects
        .filter(id_pelicula__in=dislikes_ids)
        .prefetch_related("generos", "directores", "actores")
    )

    for pelicula in peliculas_dislike:
        for genero in pelicula.generos.all():
            generos_negativos[genero.id_genero] += 7

        for director in pelicula.directores.all():
            directores_negativos[director.id_director] += 5

        for actor in pelicula.actores.all():
            actores_negativos[actor.id_actor] += 4

    excluir_ids = set(likes_ids + dislikes_ids + favoritos_ids + watchlist_ids)

    candidatas = (
        Pelicula.objects
        .exclude(id_pelicula__in=excluir_ids)
        .prefetch_related("generos", "directores", "actores", "plataformas")
        .annotate(
            total_likes=Count("calificacion", filter=Q(calificacion__reaccion="like")),
            total_dislikes=Count("calificacion", filter=Q(calificacion__reaccion="dislike")),
        )
    )

    recomendaciones = []

    for pelicula in candidatas:
        score = 0
        razones = []

        generos = list(pelicula.generos.all())
        directores = list(pelicula.directores.all())
        actores = list(pelicula.actores.all())
        plataformas = list(pelicula.plataformas.all())

        puntos_genero = sum(pesos_generos[g.id_genero] for g in generos)
        puntos_director = sum(pesos_directores[d.id_director] for d in directores)
        puntos_actor = sum(pesos_actores[a.id_actor] for a in actores)
        puntos_plataforma = sum(pesos_plataformas[p.id_plataforma] for p in plataformas)

        castigo_genero = sum(generos_negativos[g.id_genero] for g in generos)
        castigo_director = sum(directores_negativos[d.id_director] for d in directores)
        castigo_actor = sum(actores_negativos[a.id_actor] for a in actores)

        score += puntos_genero
        score += puntos_director
        score += puntos_actor
        score += puntos_plataforma

        score -= castigo_genero
        score -= castigo_director
        score -= castigo_actor

        score += min(pelicula.total_likes * 1.5, 12)
        score -= min(pelicula.total_dislikes * 2, 10)

        if pelicula.id_pelicula in visitas_ids[:10]:
            score -= 3

        if puntos_genero > 0:
            razones.append("coincide con tus géneros")

        if puntos_director > 0:
            razones.append("comparte directores afines")

        if puntos_actor > 0:
            razones.append("comparte actores relacionados")

        if puntos_plataforma > 0:
            razones.append("encaja con plataformas similares")

        if pelicula.total_likes > 0:
            razones.append("tiene buena recepción")

        if score > 0:
            pelicula.score_recomendacion = round(score, 2)
            pelicula.motivo_recomendacion = " · ".join(razones[:2]) if razones else "recomendación exploratoria"
            recomendaciones.append(pelicula)

    recomendaciones.sort(
        key=lambda p: (
            p.score_recomendacion,
            p.total_likes,
            -p.total_dislikes,
            p.nombre
        ),
        reverse=True
    )

    generos_relevantes = Genero.objects.filter(
        id_genero__in=list(pesos_generos.keys())[:12]
    ).order_by("nombre")

    return recomendaciones[:limite], generos_relevantes