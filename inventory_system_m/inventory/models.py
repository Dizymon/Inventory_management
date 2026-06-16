from django.db import models
from django.db.models import Max
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Item(models.Model):
    UNIT_CHOICES = [
        ('piece', 'Piece'), ('ream', 'Ream'), ('box', 'Box'),
        ('pack', 'Pack'), ('roll', 'Roll'), ('set', 'Set'),
        ('bundle', 'Bundle'), ('can', 'Can'), ('pair', 'Pair'),
        ('bottle', 'Bottle'), ('pad', 'Pad'),
    ]
    stock_number = models.IntegerField(unique=True)
    item_code = models.CharField(max_length=100, blank=True)
    item_name = models.CharField(max_length=255, blank=True, default='')
    description = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    unit_of_measure = models.CharField(max_length=20, choices=UNIT_CHOICES, default='piece')
    quantity = models.IntegerField(default=0)
    minimum_quantity = models.IntegerField(default=10, help_text="Low stock threshold")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        label = self.item_name or self.description
        return f"[{self.stock_number}] {label}"

    def save(self, *args, **kwargs):
        """
        Assign the smallest available positive integer to `stock_number` when not provided.
        This fills gaps left by deleted items (e.g., if 13 was deleted, the next created
        item will receive 13).
        """
        if not getattr(self, 'stock_number', None):
            # Collect existing stock numbers and find the smallest missing positive integer.
            existing = list(Item.objects.values_list('stock_number', flat=True).order_by('stock_number'))
            existing_set = set(n for n in existing if isinstance(n, int) and n > 0)
            next_sn = 1
            while next_sn in existing_set:
                next_sn += 1
            self.stock_number = next_sn
        super().save(*args, **kwargs)

    @property
    def stock_status(self):
        if self.quantity == 0:
            return 'out_of_stock'
        elif self.quantity <= self.minimum_quantity:
            return 'low_stock'
        return 'in_stock'

    @property
    def total_value(self):
        return self.quantity * self.unit_price

    class Meta:
        ordering = ['stock_number']


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
    ]
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantity = models.IntegerField()
    previous_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.item.description} - {self.transaction_type} ({self.quantity})"

    class Meta:
        ordering = ['-timestamp']


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance)
