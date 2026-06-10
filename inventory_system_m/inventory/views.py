from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta
import csv, json
from .models import Item, Transaction, Category, UserProfile
from .forms import ItemForm, TransactionForm, UserCreateForm, CategoryForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'inventory/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def get_role(user):
    try:
        return user.profile.role
    except:
        return 'user'


@login_required
def dashboard(request):
    role = get_role(request.user)
    total_items = Item.objects.count()
    out_of_stock = Item.objects.filter(quantity=0).count()
    low_stock = Item.objects.filter(quantity__gt=0, quantity__lte=models_min_qty()).count()
    recent_transactions = Transaction.objects.select_related('item', 'performed_by')[:10]
    low_stock_items = Item.objects.filter(quantity__gt=0).filter(quantity__lte=10)[:5]
    out_items = Item.objects.filter(quantity=0)[:5]
    context = {
        'role': role,
        'total_items': total_items,
        'out_of_stock': out_of_stock,
        'low_stock_count': Item.objects.filter(quantity__gt=0, quantity__lte=10).count(),
        'recent_transactions': recent_transactions,
        'low_stock_items': low_stock_items,
        'out_items': out_items,
    }
    return render(request, 'inventory/dashboard.html', context)


def models_min_qty():
    return 10


@login_required
def item_list(request):
    role = get_role(request.user)
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    category_id = request.GET.get('category', '')
    items = Item.objects.all()
    if query:
        items = items.filter(
            Q(item_name__icontains=query) |
            Q(description__icontains=query) |
            Q(item_code__icontains=query)
        )
    if status == 'low':
        items = items.filter(quantity__gt=0, quantity__lte=10)
    elif status == 'out':
        items = items.filter(quantity=0)
    elif status == 'ok':
        items = items.filter(quantity__gt=10)
    if category_id:
        items = items.filter(category_id=category_id)
    categories = Category.objects.all().order_by('name')
    return render(request, 'inventory/item_list.html', {
        'items': items,
        'role': role,
        'query': query,
        'status': status,
        'category_id': category_id,
        'categories': categories,
    })


@login_required
def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    transactions = item.transactions.select_related('performed_by')[:20]
    role = get_role(request.user)
    return render(request, 'inventory/item_detail.html', {
        'item': item, 'transactions': transactions, 'role': role
    })


@login_required
def item_create(request):
    role = get_role(request.user)
    if role not in ['admin', 'supplier']:
        messages.error(request, 'You do not have permission to add items.')
        return redirect('item_list')
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, f'Item "{item.description}" created successfully.')
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'inventory/item_form.html', {'form': form, 'action': 'Create', 'role': role})


@login_required
def item_edit(request, pk):
    role = get_role(request.user)
    if role != 'admin':
        messages.error(request, 'Only admins can edit items.')
        return redirect('item_list')
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'Item updated successfully.')
            return redirect('item_detail', pk=pk)
    else:
        form = ItemForm(instance=item)
    return render(request, 'inventory/item_form.html', {'form': form, 'item': item, 'action': 'Edit', 'role': role})


@login_required
def item_delete(request, pk):
    role = get_role(request.user)
    if role != 'admin':
        messages.error(request, 'Only admins can delete items.')
        return redirect('item_list')
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        name = item.description
        item.delete()
        messages.success(request, f'Item "{name}" deleted.')
        return redirect('item_list')
    return render(request, 'inventory/item_confirm_delete.html', {'item': item, 'role': role})


@login_required
def transaction_create(request, pk):
    role = get_role(request.user)
    if role != 'admin':
        messages.error(request, 'Only admins can log transactions.')
        return redirect('item_detail', pk=pk)
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            tx = form.save(commit=False)
            tx.item = item
            tx.performed_by = request.user
            tx.previous_quantity = item.quantity
            if tx.transaction_type == 'in':
                item.quantity += tx.quantity
            elif tx.transaction_type == 'out':
                if tx.quantity > item.quantity:
                    messages.error(request, 'Cannot remove more than available stock.')
                    return render(request, 'inventory/transaction_form.html', {'form': form, 'item': item, 'role': role})
                item.quantity -= tx.quantity
            else:
                item.quantity = tx.quantity
            tx.new_quantity = item.quantity
            item.save()
            tx.save()
            messages.success(request, 'Transaction logged successfully.')
            return redirect('item_detail', pk=pk)
    else:
        form = TransactionForm()
    return render(request, 'inventory/transaction_form.html', {'form': form, 'item': item, 'role': role})


@login_required
def reports(request):
    role = get_role(request.user)
    items = Item.objects.all()
    low_stock_items = items.filter(quantity__gt=0, quantity__lte=10)
    out_of_stock_items = items.filter(quantity=0)
    recent_txs = Transaction.objects.select_related('item', 'performed_by').order_by('-timestamp')[:50]
    total_value = sum(i.total_value for i in items)
    context = {
        'role': role,
        'items': items,
        'low_stock_items': low_stock_items,
        'out_of_stock_items': out_of_stock_items,
        'recent_txs': recent_txs,
        'total_items': items.count(),
        'total_value': total_value,
        'out_count': out_of_stock_items.count(),
        'low_count': low_stock_items.count(),
    }
    return render(request, 'inventory/reports.html', context)


@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Stock #', 'Item Code', 'Description', 'Unit', 'Quantity', 'Min Qty', 'Status', 'Unit Price', 'Total Value'])
    for item in Item.objects.all():
        writer.writerow([
            item.stock_number, item.item_code, item.description,
            item.unit_of_measure, item.quantity, item.minimum_quantity,
            item.stock_status, item.unit_price, item.total_value
        ])
    return response


@login_required
def user_management(request):
    role = get_role(request.user)
    if role != 'admin':
        messages.error(request, 'Only admins can manage users.')
        return redirect('dashboard')
    from django.contrib.auth.models import User
    users = User.objects.select_related('profile').all()
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            UserProfile.objects.create(user=user, role=form.cleaned_data['role'])
            messages.success(request, f'User {user.username} created.')
            return redirect('user_management')
    else:
        form = UserCreateForm()
    return render(request, 'inventory/user_management.html', {'users': users, 'form': form, 'role': role})


@login_required
def category_list(request):
    role = get_role(request.user)
    if role != 'admin':
        messages.error(request, 'Only admins can manage categories.')
        return redirect('dashboard')
    categories = Category.objects.all().order_by('name')
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'inventory/category_list.html', {
        'role': role,
        'categories': categories,
        'form': form,
    })


@login_required
def category_create(request):
    return category_list(request)


@login_required
def category_edit(request, pk):
    role = get_role(request.user)
    if role != 'admin':
        messages.error(request, 'Only admins can manage categories.')
        return redirect('dashboard')
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'inventory/category_form.html', {
        'role': role,
        'form': form,
        'category': category,
    })
