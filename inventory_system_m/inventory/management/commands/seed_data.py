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
            user, created = User.objects.get_or_create(username=username, defaults={'email': email})
            if created:
                user.set_password(password)
                if role == 'admin':
                    user.is_staff = True
                    user.is_superuser = True
                user.email = email
                user.save()
                UserProfile.objects.create(user=user, role=role)
                self.stdout.write(f'Created user: {username} ({role})')
            else:
                if role == 'admin' and not (user.is_staff and user.is_superuser):
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                UserProfile.objects.get_or_create(user=user, defaults={'role': role})
                self.stdout.write(f'User already exists: {username}')

        self.stdout.write(self.style.SUCCESS('Seed complete!'))
