from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('planes/', views.planes_view, name='planes'),
    path('mimundo/', views.mi_mundo_view, name='mi_mundo'),
    path('recomendaciones/', views.recomendaciones_view, name='recomendaciones'),
    path('cambiar-contrasena/', views.cambiar_contrasena_view, name='cambiar_contrasena'),
]
