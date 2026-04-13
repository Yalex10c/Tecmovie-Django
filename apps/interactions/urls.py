from django.urls import path
from . import views

app_name = 'interactions'

urlpatterns = [
    path('favorite/<int:movie_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('watchlist/<int:movie_id>/', views.toggle_watchlist, name='toggle_watchlist'),
    path('rate/<int:movie_id>/', views.rate_movie, name='rate_movie'),
]
