# SIB Backend

Django-based backend system for inventory and business management.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Navigate to backend**
```bash
cd backend/sib
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run migrations**
```bash
python manage.py migrate
```

4. **Set up permissions**
```bash
python manage.py setup_groups
python manage.py fix_permissions --fix-all
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Start server**
```bash
python manage.py runserver
```

Server runs at `http://localhost:8000`

## 📁 Project Structure

```
backend/sib/
├── sib/                    # Django project
├── users_app/             # User management
├── inventory_app/         # Inventory management
├── sales_app/            # Sales and orders
├── production_app/       # Production management
├── warehouse/            # Warehouse management
├── communication_app/    # Messaging system
├── logs_app/            # Activity logging
└── manage.py            # Django management script
```

## 👥 User Groups

- **Commerciaux**: View stock, manage orders, track customers
- **Magasiniers**: View stock, process orders, confirm production
- **Ouvriers de production**: View orders, update production status
- **Administrateurs**: Full system access

## 🔌 API Endpoints

### Authentication
- `POST /api/token/` - Get authentication token

### Users
- `GET /api/v1/users/utilisateurs/` - List users (Admin only)
- `POST /api/v1/users/utilisateurs/` - Create user (Admin only)
- `GET /api/v1/users/me/` - Get current user profile

### Inventory
- `GET /api/v1/inventory/matieres-premieres/` - Raw materials
- `GET /api/v1/inventory/produits-finis/` - Finished products
- `GET /api/v1/inventory/mouvements-stock/` - Stock movements
- `GET /api/v1/inventory/stock/` - Current stock levels

### Sales
- `GET /api/v1/sales/clients/` - Customers
- `POST /api/v1/sales/clients/` - Create customer
- `GET /api/v1/sales/commandes/` - Orders
- `POST /api/v1/sales/commandes/` - Create order

### Production
- `GET /api/v1/production/productions/` - Production orders
- `POST /api/v1/production/productions/` - Create production order

### Warehouse
- `GET /api/v1/warehouse/entrepots/` - Warehouses
- `POST /api/v1/warehouse/entrepots/` - Create warehouse

### Communication
- `GET /api/v1/communication/messages/` - Messages
- `POST /api/v1/communication/messages/` - Send message

## 🛠️ Management Commands

### Setup
```bash
# Set up user groups
python manage.py setup_groups

# Fix permissions
python manage.py fix_permissions --fix-all

# Set up warehouse permissions
python manage.py setup_warehouse_permissions
```

### User Management
```bash
# List users and groups
python manage.py assign_users_to_groups --list-users

# Assign user to group
python manage.py assign_users_to_groups --username user --group Commerciaux

# Fix users without groups
python manage.py assign_users_to_groups --fix-all
```

### Database
```bash
# Create tables
python manage.py migrate

# Backup data
python manage.py dumpdata > backup.json
```

## 🔒 Security

- Token-based API authentication
- Group-based permissions
- Session-based admin authentication
- CSRF protection enabled

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users_app
python manage.py test inventory_app
```

## 🔧 Troubleshooting

### Common Issues

1. **Permission Errors**
   - Run `python manage.py fix_permissions --fix-all`

2. **Database Errors**
   - Run `python manage.py migrate`

3. **Import Errors**
   - Install dependencies: `pip install -r requirements.txt`

### Debug Mode
Enable in settings for detailed error messages:
```python
DEBUG = True
```

## 📝 API Usage

### Authentication
Include token in headers:
```
Authorization: Token your-token-here
```

### Creating Users
```json
POST /api/v1/users/utilisateurs/
{
  "user_data": {
    "username": "newuser",
    "email": "user@example.com",
    "password": "password123"
  },
  "nom": "User Name",
  "group_name": "Commerciaux"
}
```

### Response Format
```json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2"
}
```

## 🚀 Deployment

### Production Setup
1. Set `DEBUG=False`
2. Configure production database
3. Set up static file serving
4. Configure HTTPS
5. Set up logging

## 📞 Support

For issues:
1. Check troubleshooting section
2. Review Django logs
3. Verify user permissions
