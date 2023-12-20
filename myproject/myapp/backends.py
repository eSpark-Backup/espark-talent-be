from django.contrib.auth.backends import BaseBackend
from .models import Client

class CustomBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = Client.objects.get(email=email)
        except Client.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        else:
            return None