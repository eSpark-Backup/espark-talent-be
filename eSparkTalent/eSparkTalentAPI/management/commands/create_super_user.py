from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os
from dotenv import load_dotenv


load_dotenv()

class Command(BaseCommand):
    help = 'Create superusers if none exist'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        superusers = [
            {'username': 'database admin', 'email': os.getenv('DATABASE_ADMIN_EMAIL'), 'password': os.getenv('DATABASE_ADMIN_AUTH')},
            {'username': 'super_admin', 'email': os.getenv('SUPER_ADMIN_EMAIL'), 'password': os.getenv('SUPER_ADMIN_AUTH')}
        ]

        for superuser in superusers:
            if not User.objects.filter(username=superuser['username']).exists():
                User.objects.create_superuser(
                    username=superuser['username'],
                    email=superuser['email'],
                    password=superuser['password']
                )
                self.stdout.write(self.style.SUCCESS(f"Superuser {superuser['username']} created."))
            else:
                self.stdout.write(self.style.SUCCESS(f"Superuser {superuser['username']} already exists."))
