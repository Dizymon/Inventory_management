from django.contrib import admin
from .models import Item, Transaction, Category, UserProfile

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['stock_number', 'item_name', 'description', 'unit_of_measure', 'quantity', 'stock_status', 'item_code']
    search_fields = ['item_name', 'description', 'item_code']
    list_filter = ['unit_of_measure', 'category']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['item', 'transaction_type', 'quantity', 'performed_by', 'timestamp']
    list_filter = ['transaction_type']

admin.site.register(Category)
admin.site.register(UserProfile)
