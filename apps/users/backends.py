from django.contrib.auth.backends import ModelBackend
from .models import Usuario


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = username or kwargs.get('email')

        if email is None or password is None:
            return None

        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None