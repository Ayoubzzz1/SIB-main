#!/usr/bin/env python3
"""
Test script to verify that the permission system is working correctly.
This script tests user creation with groups and permission verification.
"""

import os
import sys
import django
from django.conf import settings

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'sib'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sib.settings')
django.setup()

from django.contrib.auth.models import User, Group
from django.test import RequestFactory
from users_app.models import Utilisateur
from users_app.permissions import HasGroupPermission, CanManageUsers, CanViewStock
from users_app.serializers import UtilisateurSerializer

def test_user_creation_with_group():
    """Test creating a user with a specific group"""
    print("🧪 Testing user creation with group assignment...")
    
    # Test data
    user_data = {
        'user_data': {
            'username': 'test_commercial',
            'email': 'test_commercial@example.com',
            'password': 'testpass123'
        },
        'nom': 'Test Commercial User',
        'group_name': 'Commerciaux'
    }
    
    try:
        # Create user using serializer
        serializer = UtilisateurSerializer(data=user_data)
        if serializer.is_valid():
            user = serializer.save()
            print(f"✅ User created successfully: {user.nom}")
            
            # Check if user was assigned to the correct group
            groups = user.user.groups.all()
            if groups.exists():
                group_names = [g.name for g in groups]
                print(f"✅ User assigned to groups: {group_names}")
                
                if 'Commerciaux' in group_names:
                    print("✅ User correctly assigned to Commerciaux group")
                else:
                    print("❌ User not assigned to Commerciaux group")
            else:
                print("❌ User not assigned to any groups")
                
            # Clean up - delete the test user
            user.user.delete()
            print("🧹 Test user cleaned up")
            
        else:
            print(f"❌ User creation failed: {serializer.errors}")
            
    except Exception as e:
        print(f"❌ Error during user creation test: {e}")

def test_permission_classes():
    """Test that permission classes work correctly"""
    print("\n🔐 Testing permission classes...")
    
    # Get a test user from each group
    groups = Group.objects.all()
    factory = RequestFactory()
    
    for group in groups:
        users = group.user_set.all()
        if users.exists():
            test_user = users.first()
            print(f"\n👤 Testing permissions for user '{test_user.username}' in group '{group.name}':")
            
            # Test HasGroupPermission
            permission = HasGroupPermission()
            permission.required_groups = [group.name]
            
            request = factory.get('/')
            request.user = test_user
            
            if permission.has_permission(request, None):
                print(f"   ✅ HasGroupPermission working for {group.name}")
            else:
                print(f"   ❌ HasGroupPermission not working for {group.name}")
            
            # Test specific permission classes
            if group.name == 'Administrateurs':
                admin_permission = CanManageUsers()
                if admin_permission.has_permission(request, None):
                    print(f"   ✅ CanManageUsers working for {group.name}")
                else:
                    print(f"   ❌ CanManageUsers not working for {group.name}")
            
            if group.name in ['Commerciaux', 'Magasiniers', 'Ouvriers de production']:
                stock_permission = CanViewStock()
                if stock_permission.has_permission(request, None):
                    print(f"   ✅ CanViewStock working for {group.name}")
                else:
                    print(f"   ❌ CanViewStock not working for {group.name}")

def test_existing_users():
    """Test existing users and their group assignments"""
    print("\n👥 Checking existing users and their groups...")
    
    users = User.objects.all()
    users_without_groups = []
    users_without_profiles = []
    
    for user in users:
        groups = user.groups.all()
        group_names = [g.name for g in groups] if groups.exists() else []
        
        try:
            profile = user.utilisateur
            profile_status = f"Profile: {profile.nom}"
        except Utilisateur.DoesNotExist:
            profile_status = "❌ No profile"
            users_without_profiles.append(user)
        
        if not groups.exists() and not user.is_superuser:
            users_without_groups.append(user)
            print(f"⚠️  {user.username}: No groups | {profile_status}")
        else:
            print(f"✅ {user.username}: {group_names} | {profile_status}")
    
    if users_without_groups:
        print(f"\n⚠️  Found {len(users_without_groups)} users without groups")
    else:
        print("\n✅ All users have groups assigned")
    
    if users_without_profiles:
        print(f"⚠️  Found {len(users_without_profiles)} users without profiles")
    else:
        print("✅ All users have profiles")

def main():
    """Run all tests"""
    print("🚀 Starting permission system tests...")
    print("=" * 50)
    
    # Check if groups exist
    groups = Group.objects.all()
    if not groups.exists():
        print("❌ No groups found! Please run 'python manage.py setup_groups' first.")
        return
    
    print(f"✅ Found {groups.count()} groups: {[g.name for g in groups]}")
    
    # Run tests
    test_existing_users()
    test_permission_classes()
    test_user_creation_with_group()
    
    print("\n" + "=" * 50)
    print("🎯 Permission system test completed!")
    print("\n💡 If you see any issues, run:")
    print("   python manage.py fix_permissions --fix-all")

if __name__ == '__main__':
    main()
