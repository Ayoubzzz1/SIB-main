# SIB Backend

Django backend for SIB Management System with Jazzmin admin interface.

## 🚀 Quick Setup

1. **Install dependencies:**
   ```bash
   cd backend/sib
   pip install -r requirements.txt
   ```

2. **Create .env file:**
   ```bash
   # Create .env file with your SECRET_KEY
   SECRET_KEY=your-strong-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Start server:**
   ```bash
   python manage.py runserver
   ```

## 📁 Project Structure

```
backend/
├── README.md
├── requirements.txt
├── .gitignore
└── sib/
    ├── manage.py
    ├── db.sqlite3
    ├── sib/
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── middleware.py
    ├── static/
    │   └── images/
    │       └── logo.png
    ├── templates/
    ├── users_app/
    ├── inventory_app/
    ├── sales_app/
    ├── production_app/
    ├── communication_app/
    ├── logs_app/
    └── warehouse/
```

## ✨ Features

- **User Management**: Warehouse access control
- **Inventory Management**: Materials, products, stock movements
- **Sales Management**: Orders, clients, suppliers
- **Production Management**: Production orders and tracking
- **Communication System**: Internal messaging
- **Activity Logging**: System activity tracking
- **Modern Admin**: Jazzmin with red theme

## 🔐 Security

- Environment variables for sensitive settings
- CORS protection
- XSS protection
- CSRF protection
- Secure headers

## 🌐 Admin Interface

Access at: http://127.0.0.1:8000/admin/

Uses Django Jazzmin with custom red theme and icons.
