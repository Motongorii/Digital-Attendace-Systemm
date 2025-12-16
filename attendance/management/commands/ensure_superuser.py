from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or update a superuser non-interactively"

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True, help='Username for the superuser')
        parser.add_argument('--password', required=True, help='Password for the superuser')
        parser.add_argument('--email', default='admin@example.com', help='Email for the superuser')

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        password = options['password']
        email = options['email']

        user = User.objects.filter(username=username).first()
        if user:
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.email = email
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated superuser "{username}"'))
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Created superuser "{username}"'))
