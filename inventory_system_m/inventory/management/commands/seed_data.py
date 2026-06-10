from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import UserProfile


class Command(BaseCommand):
    help = 'Seed default admin, supplier, and user accounts'

    def handle(self, *args, **kwargs):
        users_data = [
            ('admin_user', 'admin123', 'admin', 'admin@inventory.local'),
            ('supplier_user', 'supplier123', 'supplier', 'supplier@inventory.local'),
            ('regular_user', 'user123', 'user', 'user@inventory.local'),
        ]

        for username, password, role, email in users_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=password, email=email)
                UserProfile.objects.create(user=user, role=role)
                self.stdout.write(f'Created user: {username} ({role})')
            else:
                self.stdout.write(f'User already exists: {username}')

        self.stdout.write(self.style.SUCCESS('Seed complete!'))
