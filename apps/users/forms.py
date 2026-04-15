from django import forms
from django.contrib.auth import authenticate
from .models import Usuario
from apps.movies.models import Genero


class LoginForm(forms.Form):
    correo = forms.EmailField()
    contrasena = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        correo = cleaned_data.get('correo')
        contrasena = cleaned_data.get('contrasena')

        if correo and contrasena:
            user = authenticate(username=correo, password=contrasena)
            if user is None:
                raise forms.ValidationError("Correo o contraseña incorrectos.")

            cleaned_data['user'] = user

        return cleaned_data


class RegisterForm(forms.Form):
    nombre = forms.CharField(max_length=150)
    correo = forms.EmailField()
    contrasena = forms.CharField(widget=forms.PasswordInput)

    def clean_correo(self):
        correo = self.cleaned_data['correo']
        if Usuario.objects.filter(email=correo).exists():
            raise forms.ValidationError("El correo ya está registrado.")
        return correo


class MiMundoForm(forms.Form):
    generos = forms.ModelMultipleChoiceField(
        queryset=Genero.objects.all().order_by('nombre'),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )