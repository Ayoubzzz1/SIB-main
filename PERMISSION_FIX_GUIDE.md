# Permission System Fix Guide

## Problem Description

The issue was that when users were created, they were not being assigned to Django groups properly. This caused users to have no permissions even though they were created with specific roles. The system was migrated from using a `role` field to using Django groups, but the user creation process wasn't updated.

## What Was Fixed

### 1. Updated User Serializer (`backend/sib/users_app/serializers.py`)

- **Added `group_name` field**: Users can now specify which Django group they should be assigned to during creation
- **Updated `create()` method**: Now assigns users to the specified group when creating them
- **Updated `update()` method**: Allows changing user groups when updating profiles
- **Removed references to old `role` field**: The system now uses Django groups exclusively

### 2. Fixed Views (`backend/sib/users_app/views.py` and `backend/sib/communication_app/views.py`)

- **Updated permission checks**: Changed from checking `user.utilisateur.role` to checking Django groups
- **Improved admin detection**: Now checks for superuser, staff, or membership in 'Administrateurs' group

### 3. Enhanced User Signals (`backend/sib/users_app/signals.py`)

- **Automatic group assignment**: New users are automatically assigned to the 'Commerciaux' group if no group is specified
- **Prevents permission issues**: Ensures users always have at least basic permissions

### 4. Created Management Commands

#### `fix_permissions` Command
```bash
# Fix all permission issues at once
python manage.py fix_permissions --fix-all

# Set up groups only
python manage.py fix_permissions --setup-groups

# Assign users to groups only
python manage.py fix_permissions --assign-users
```

#### `assign_users_to_groups` Command
```bash
# List all users and their groups
python manage.py assign_users_to_groups --list-users

# Assign a specific user to a group
python manage.py assign_users_to_groups --username john --group Commerciaux

# Fix all users without groups
python manage.py assign_users_to_groups --fix-all
```

## How to Fix Your Current System

### Step 1: Set Up Groups
```bash
cd backend/sib
python manage.py setup_groups
```

### Step 2: Fix Existing Users
```bash
python manage.py fix_permissions --fix-all
```

### Step 3: Verify the Fix
```bash
python manage.py assign_users_to_groups --list-users
```

### Step 4: Test the System
```bash
python test_permissions.py
```

## Available Groups and Permissions

### 1. Commerciaux (Commercial Users)
- **Permissions**: View stock, create and manage customer orders, track customers
- **Default group**: New users are assigned here if no group is specified

### 2. Magasiniers (Warehouse Workers)
- **Permissions**: View stock, process orders, confirm and forward to production

### 3. Ouvriers de production (Production Workers)
- **Permissions**: View confirmed orders, view raw materials stock, update production status

### 4. Administrateurs (Administrators)
- **Permissions**: Full system access, user management, all operations

## Creating Users with Proper Permissions

### Via API
```json
{
  "user_data": {
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepassword"
  },
  "nom": "New User Name",
  "group_name": "Commerciaux"
}
```

### Via Django Admin
1. Go to Django Admin → Users
2. Create a new user
3. In the "Groups" section, select the appropriate group
4. Save the user

## Testing the Fix

Run the test script to verify everything is working:
```bash
python test_permissions.py
```

This will:
- Check existing users and their group assignments
- Test permission classes for each group
- Create a test user with group assignment
- Verify that permissions are working correctly

## Troubleshooting

### Users Still Have No Permissions
1. Check if groups exist: `python manage.py assign_users_to_groups --list-users`
2. If no groups exist, run: `python manage.py setup_groups`
3. Assign users to groups: `python manage.py fix_permissions --assign-users`

### Permission Classes Not Working
1. Verify groups have permissions: Check Django Admin → Groups
2. Ensure users are assigned to groups
3. Test with the test script: `python test_permissions.py`

### API Errors
1. Check that the `group_name` field is provided when creating users
2. Verify the group name matches exactly (case-sensitive)
3. Ensure the group exists in the database

## Migration Notes

- The old `role` field has been completely removed
- All permission checks now use Django groups
- Existing users without groups will be assigned to 'Commerciaux' by default
- The system is backward compatible with existing group-based permissions

## Security Considerations

- Users without groups have no permissions
- Superusers and staff users have full access regardless of groups
- Group permissions are enforced at the view level
- Warehouse-specific permissions are handled separately through the `UtilisateurEntrepot` model
