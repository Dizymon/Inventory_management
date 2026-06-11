# InvenTrack — Inventory Management System

A Django-based inventory system with Admin, Supplier, and User roles.

## Overview

This project supports:
- role-based access control
- inventory tracking with stock status
- categories, item details, and transactions
- login/logout and dashboard reporting
- full admin user management

## Roles

| Role     | Description |
|----------|-------------|
| Admin    | Add/edit/delete inventory, manage users/categories, view reports |
| Supplier | Add inventory items and view item details |
| Viewer   | Read-only access to inventory and item details |

## Setup

1. Install dependencies
```bash
pip install django
```

2. Run migrations
```bash
python manage.py migrate
```

3. Seed default users
```bash
python manage.py seed_data
```

4. Run the development server
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000 and log in.

## Default Accounts

| Username      | Password      | Role     |
|---------------|---------------|----------|
| admin         | admin123      | Admin    |
| supplier      | supplier123   | Supplier |
| viewer        | viewer123     | User     |
| Database      | DB123         | Superuser|

## Features

- Dashboard with total item count, low stock count, out of stock count, and recent transactions
- Inventory list with search, category filter, and stock status filter
- Item detail page with stock status and transaction history
- Admin-only delete and category/user management
- Supplier item creation with price and stock details
- Role-based UI and access control

## Stock Status Logic

- **Out of Stock** — quantity = 0
- **Low Stock** — quantity > 0 and quantity ≤ minimum_quantity
- **In Stock** — quantity > minimum_quantity

## Notes

- The seed command now only creates default user accounts and does not pre-populate inventory items.
- Use the Admin or Supplier accounts to add inventory items after setup.
