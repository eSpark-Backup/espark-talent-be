from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create superusers if none exist'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        superusers = [
            {'username': 'database admin', 'email': 'talent@backendpython.com', 'password': 'talent$90waqar$'},
            {'username': 'super_admin', 'email': 'superadmin@esparkconsultants.com', 'password': 'super@espark'}
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
