# Migration Guide: SQLite to XAMPP MySQL

## 🔄 **Step-by-Step Migration Process**

### 1. **Install XAMPP**
- Download and install XAMPP from: https://www.apachefriends.org/
- Start Apache and MySQL services in XAMPP Control Panel

### 2. **Create MySQL Database**
1. Open phpMyAdmin: http://localhost/phpmyadmin
2. Create a new database named `sib_db`
3. Set character set to `utf8mb4_unicode_ci`

### 3. **Install MySQL Dependencies**
```bash
cd backend/sib
pip install mysqlclient
```

### 4. **Update .env File**
Create or update your `.env` file with MySQL settings:

```env
# Database Settings for XAMPP MySQL
DB_ENGINE=django.db.backends.mysql
DB_NAME=sib_db
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306

# Other settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

### 5. **Export Data from SQLite (Optional)**
If you have existing data in SQLite:

```bash
# Export data to JSON
python manage.py dumpdata > data_backup.json
```

### 6. **Create MySQL Tables**
```bash
# Create new tables in MySQL
python manage.py makemigrations
python manage.py migrate
```

### 7. **Import Data (If you exported)**
```bash
# Import data from JSON backup
python manage.py loaddata data_backup.json
```

### 8. **Create Superuser**
```bash
python manage.py createsuperuser
```

### 9. **Test the Migration**
```bash
python manage.py runserver
```

## ⚠️ **Important Notes**

### **XAMPP Configuration:**
- **Default MySQL Port**: 3306
- **Default Username**: root
- **Default Password**: (empty)
- **Host**: localhost

### **Common Issues & Solutions:**

1. **MySQL Connection Error:**
   - Make sure XAMPP MySQL service is running
   - Check if port 3306 is not blocked

2. **Character Set Issues:**
   - Database is already configured for UTF-8
   - MySQL options are set in settings.py

3. **Permission Issues:**
   - Make sure MySQL user has proper permissions
   - For XAMPP, root user should work fine

### **Performance Benefits:**
- ✅ Better for concurrent users
- ✅ More robust data integrity
- ✅ Better backup and recovery
- ✅ Scalable for production

### **Backup Strategy:**
```bash
# Regular backup command
python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json
```

## 🚀 **Production Considerations**

For production deployment:
1. Use a dedicated MySQL user (not root)
2. Set strong passwords
3. Configure proper MySQL security settings
4. Set up regular backups
5. Use connection pooling for better performance

