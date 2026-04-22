from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.home_top_peliculas, name='home'),
    #path('nuevas/', views.nuevas_peliculas, name='nuevas'),
    path('tendencias/', views.tendencias_peliculas, name='tendencias'),
    path('pelicula/<int:id>/', views.detalle_pelicula, name='detalle'),

    path('actores/', views.lista_actores, name='actores'),
    path('actor/<int:id>/', views.detalle_actor, name='detalle_actor'),
]