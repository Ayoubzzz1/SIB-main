# Warehouse Permissions System Guide

## Overview

The warehouse permissions system allows you to control which users have access to specific warehouses and what operations they can perform. This system provides granular control over warehouse access while maintaining simplicity with checkbox-based permissions.

## Features

### 1. User-Warehouse Relationship
- **Global Access**: Users can have access to all warehouses
- **Specific Access**: Users can have access to only specific warehouses
- **Granular Permissions**: For each warehouse, users can have different permission levels

### 2. Permission Types
Each user-warehouse relationship has three simple boolean permissions:

- **Peut lire** (Can Read): User can view data from this warehouse
- **Peut modifier** (Can Modify): User can create and update data in this warehouse  
- **Peut supprimer** (Can Delete): User can delete data from this warehouse

### 3. Role-Based Access
- **Admin**: Always has full access to all warehouses
- **Magasinier**: Can manage warehouse operations (with warehouse-specific permissions)
- **Commercial**: Can view warehouse data (with warehouse-specific permissions)
- **Production**: Can view and modify warehouse data (with warehouse-specific permissions)

## Database Structure

### Utilisateur Model
```python
class Utilisateur(models.Model):
    # ... existing fields ...
    acces_tous_entrepots = models.BooleanField(
        default=False, 
        verbose_name="Accès à tous les entrepôts"
    )
```

### UtilisateurEntrepot Model
```python
class UtilisateurEntrepot(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, ...)
    entrepot = models.ForeignKey('warehouse.Entrepot', ...)
    peut_lire = models.BooleanField(default=True)
    peut_modifier = models.BooleanField(default=False)
    peut_supprimer = models.BooleanField(default=False)
```

## Usage Examples

### 1. Creating a User with Warehouse Access

```python
# Create user with access to specific warehouses
utilisateur = Utilisateur.objects.create(
    user=user_instance,
    nom="John Doe",
    role="magasin",
    acces_tous_entrepots=False
)

# Give access to specific warehouses
entrepot1 = Entrepot.objects.get(nom="Magasin 1")
UtilisateurEntrepot.objects.create(
    utilisateur=utilisateur,
    entrepot=entrepot1,
    peut_lire=True,
    peut_modifier=True,
    peut_supprimer=True
)
```

### 2. Checking User Permissions

```python
# Check if user has access to a warehouse
if utilisateur.has_warehouse_access(entrepot):
    print("User has access to this warehouse")

# Check specific permissions
if utilisateur.has_warehouse_read_access(entrepot):
    print("User can read from this warehouse")

if utilisateur.has_warehouse_write_access(entrepot):
    print("User can modify data in this warehouse")

if utilisateur.has_warehouse_delete_access(entrepot):
    print("User can delete data from this warehouse")
```

### 3. Getting Accessible Warehouses

```python
# Get all warehouses user has access to
accessible_warehouses = utilisateur.get_accessible_warehouses()

# Filter stock by accessible warehouses
stock = Stock.objects.filter(entrepot__in=accessible_warehouses)
```

## Admin Interface

### User Management
1. Go to **Admin > Utilisateurs**
2. Create or edit a user
3. Set **"Accès à tous les entrepôts"** to True for global access
4. Or add specific warehouse access in the inline section

### Warehouse Permissions
1. In the user edit page, scroll to **"Accès aux entrepôts"**
2. Add warehouse entries with checkboxes for:
   - ✅ **Peut lire** (Can Read)
   - ✅ **Peut modifier** (Can Modify) 
   - ✅ **Peut supprimer** (Can Delete)

### Permission Summary
The admin interface shows a summary of permissions for each user-warehouse relationship.

## API Usage

### Creating User with Warehouse Access
```json
POST /api/users/
{
    "nom": "John Doe",
    "role": "magasin",
    "acces_tous_entrepots": false,
    "entrepots_ids": [1, 2],
    "user_data": {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "password123"
    }
}
```

### User Response with Warehouse Permissions
```json
{
    "id": 1,
    "nom": "John Doe",
    "role": "magasin",
    "acces_tous_entrepots": false,
    "entrepots_autorises": [
        {
            "id": 1,
            "entrepot": 1,
            "entrepot_nom": "Magasin 1",
            "peut_lire": true,
            "peut_modifier": true,
            "peut_supprimer": false,
            "permissions_summary": "Lecture, Modification"
        }
    ]
}
```

## Permission Classes

### CanAccessWarehouse
- Checks if user has access to a specific warehouse
- Used for general warehouse access

### CanReadWarehouse
- Checks if user has read permission for a warehouse
- Used for GET requests

### CanWriteWarehouse  
- Checks if user has write permission for a warehouse
- Used for POST, PUT, PATCH requests

### CanDeleteWarehouse
- Checks if user has delete permission for a warehouse
- Used for DELETE requests

## Frontend Integration

### User Form
Add warehouse selection to user creation/editing forms:

```jsx
// Warehouse selection component
<WarehouseSelector 
    selectedWarehouses={user.entrepots_ids}
    onChange={setSelectedWarehouses}
/>

// Permission checkboxes for each warehouse
{selectedWarehouses.map(warehouse => (
    <WarehousePermissions
        warehouse={warehouse}
        permissions={permissions[warehouse.id]}
        onChange={updatePermissions}
    />
))}
```

### Stock Filtering
Filter stock data based on user's warehouse access:

```jsx
// Only show stock from accessible warehouses
const accessibleStock = stock.filter(item => 
    user.accessibleWarehouses.includes(item.entrepot.id)
);
```

## Testing

Run the test script to see the system in action:

```bash
python test_warehouse_permissions.py
```

This will create test users with different permission levels and demonstrate how the system works.

## Migration Notes

If you're upgrading from the previous JSON-based system:

1. The `permissions` JSON field has been replaced with three boolean fields
2. Existing data will be migrated automatically
3. New users will have default permissions (read-only access)

## Best Practices

1. **Principle of Least Privilege**: Only grant the minimum permissions necessary
2. **Regular Review**: Periodically review user warehouse access
3. **Documentation**: Keep track of who has access to which warehouses
4. **Testing**: Test permissions thoroughly before deploying to production

## Troubleshooting

### Common Issues

1. **User can't see any warehouses**: Check if `acces_tous_entrepots` is False and no specific warehouses are assigned
2. **User can't modify data**: Ensure `peut_modifier` is True for the relevant warehouses
3. **Permission denied errors**: Verify the user has the correct role and warehouse permissions

### Debug Commands

```python
# Check user's accessible warehouses
user.get_accessible_warehouses()

# Check specific warehouse access
user.has_warehouse_access(entrepot)

# Check detailed permissions
user.has_warehouse_read_access(entrepot)
user.has_warehouse_write_access(entrepot)
user.has_warehouse_delete_access(entrepot)
``` 