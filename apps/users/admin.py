from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Plan, Suscripcion, MetodoPago

@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')

admin.site.register(Plan)
admin.site.register(Suscripcion)
admin.site.register(MetodoPago)
