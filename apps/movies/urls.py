from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.home_top_peliculas, name='home'),
    path('nuevas/', views.nuevas_peliculas, name='nuevas'),
    path('pelicula/<int:id>/', views.detalle_pelicula, name='detalle'),
]
