from django import forms
from django.contrib.auth.models import User
from .models import Item, Transaction, Category


class ItemForm(forms.ModelForm):
    # Allow leaving stock_number blank in the form; model.save() will auto-assign
    stock_number = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    class Meta:
        model = Item
        fields = ['stock_number', 'item_code', 'item_name', 'description', 'category',
                  'unit_of_measure', 'quantity', 'minimum_quantity', 'unit_price']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'stock_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'item_code': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'unit_of_measure': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'minimum_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'quantity', 'notes']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class UserCreateForm(forms.Form):
    ROLE_CHOICES = [('admin', 'Admin'), ('supplier', 'Supplier'), ('user', 'User')]
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    def save(self, commit=True):
        user = User(
            username=self.cleaned_data['username'],
            email=self.cleaned_data.get('email', '')
        )
        return user


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category name'}),
        }

    def clean_name(self):
        return self.cleaned_data['name'].strip()
