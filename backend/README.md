# SIB Backend

A comprehensive Django-based backend system for inventory and business management.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- SQLite (default) or PostgreSQL/MySQL

### Installation

1. **Clone and navigate to backend**
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

4. **Set up groups and permissions**
```bash
python manage.py setup_groups
python manage.py fix_permissions --fix-all
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Run the development server**
```bash
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

## 📁 Project Structure

```
backend/sib/
├── sib/                    # Main Django project
│   ├── settings.py        # Django settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── users_app/            # User management
├── inventory_app/        # Inventory management
├── sales_app/           # Sales and orders
├── production_app/      # Production management
├── warehouse/           # Warehouse management
├── communication_app/   # Messaging system
├── logs_app/           # Activity logging
├── static/             # Static files
├── templates/          # HTML templates
├── manage.py           # Django management script
└── requirements.txt    # Python dependencies
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the `backend/sib/` directory:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Configuration
The system uses SQLite by default. For production, configure PostgreSQL or MySQL in `settings.py`.

## 👥 User Management & Permissions

### User Groups
The system uses Django groups for permission management:

- **Commerciaux**: View stock, manage customer orders, track customers
- **Magasiniers**: View stock, process orders, confirm production
- **Ouvriers de production**: View confirmed orders, update production status
- **Administrateurs**: Full system access

### Creating Users
Via API:
```json
POST /api/v1/users/utilisateurs/
{
  "user_data": {
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepassword"
  },
  "nom": "User Full Name",
  "group_name": "Commerciaux"
}
```

### Managing Permissions
```bash
# List all users and their groups
python manage.py assign_users_to_groups --list-users

# Assign user to specific group
python manage.py assign_users_to_groups --username john --group Commerciaux

# Fix all users without groups
python manage.py fix_permissions --fix-all
```

## 🔌 API Endpoints

### Authentication
- `POST /api/token/` - Get authentication token
- `POST /api-auth/login/` - Login via web interface

### Users
- `GET /api/v1/users/utilisateurs/` - List users (Admin only)
- `POST /api/v1/users/utilisateurs/` - Create user (Admin only)
- `GET /api/v1/users/me/` - Get current user profile
- `PUT /api/v1/users/utilisateurs/{id}/` - Update user (Admin only)

### Inventory
- `GET /api/v1/inventory/matieres-premieres/` - Raw materials
- `GET /api/v1/inventory/produits-finis/` - Finished products
- `GET /api/v1/inventory/produits-semi-finis/` - Semi-finished products
- `GET /api/v1/inventory/mouvements-stock/` - Stock movements
- `GET /api/v1/inventory/stock/` - Current stock levels

### Sales
- `GET /api/v1/sales/clients/` - Customers
- `POST /api/v1/sales/clients/` - Create customer
- `GET /api/v1/sales/commandes/` - Orders
- `POST /api/v1/sales/commandes/` - Create order
- `GET /api/v1/sales/fournisseurs/` - Suppliers

### Production
- `GET /api/v1/production/productions/` - Production orders
- `POST /api/v1/production/productions/` - Create production order
- `GET /api/v1/production/matieres-production/` - Production materials

### Warehouse
- `GET /api/v1/warehouse/entrepots/` - Warehouses
- `POST /api/v1/warehouse/entrepots/` - Create warehouse

### Communication
- `GET /api/v1/communication/messages/` - Messages
- `POST /api/v1/communication/messages/` - Send message

## 🛠️ Management Commands

### Setup Commands
```bash
# Set up user groups with permissions
python manage.py setup_groups

# Fix permission issues
python manage.py fix_permissions --fix-all

# Set up warehouse permissions
python manage.py setup_warehouse_permissions
```

### User Management
```bash
# Create user profiles for existing users
python manage.py fix_users

# Assign users to groups
python manage.py assign_users_to_groups --list-users
```

### Database
```bash
# Create database tables
python manage.py migrate

# Create initial data
python manage.py loaddata initial_data

# Backup database
python manage.py dumpdata > backup.json
```

## 🔒 Security

### Permission Classes
- `HasGroupPermission`: Base permission for group-based access
- `CanManageUsers`: Admin-only user management
- `CanViewStock`: Stock viewing permissions
- `CanManageClients`: Customer management permissions
- `IsOwnerOrAdmin`: Object ownership permissions

### Authentication
- Token-based authentication for API
- Session-based authentication for admin interface
- Group-based permissions for all operations

## 📊 Logging

The system includes comprehensive logging:
- User actions are logged automatically
- API requests are tracked
- Error logging for debugging
- Activity logs for audit trails

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users_app
python manage.py test inventory_app
```

### API Testing
Use the provided test scripts or tools like Postman to test API endpoints.

## 🚀 Deployment

### Production Settings
1. Set `DEBUG=False` in settings
2. Configure production database
3. Set up static file serving
4. Configure HTTPS
5. Set up proper logging

### Docker (Optional)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 📝 API Documentation

### Authentication
All API requests require authentication. Include the token in headers:
```
Authorization: Token your-token-here
```

### Response Format
All API responses follow this format:
```json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Error Handling
Errors return appropriate HTTP status codes:
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## 🔧 Troubleshooting

### Common Issues

1. **Permission Denied Errors**
   - Run `python manage.py fix_permissions --fix-all`
   - Check user group assignments

2. **Database Errors**
   - Run `python manage.py migrate`
   - Check database configuration

3. **Import Errors**
   - Install missing dependencies: `pip install -r requirements.txt`
   - Check Python path

4. **API Authentication Issues**
   - Verify token is valid
   - Check user permissions

### Debug Mode
Enable debug mode in settings for detailed error messages:
```python
DEBUG = True
```

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Check Django logs for errors
4. Verify user permissions and group assignments

## 📄 License

This project is proprietary software. All rights reserved.
