#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sib.settings')
django.setup()

from django.contrib.auth.models import User
from users_app.models import Utilisateur

def setup_user():
    # Get the superuser
    user = User.objects.get(username='sib2')
    
    # Set password
    user.set_password('sib2')
    user.save()
    
    # Create Utilisateur profile if it doesn't exist
    try:
        utilisateur = user.utilisateur
        print(f"Utilisateur profile already exists for {user.username}")
    except Utilisateur.DoesNotExist:
        utilisateur = Utilisateur.objects.create(
            user=user,
            nom="SIB Admin",
            role="admin"
        )
        print(f"Created Utilisateur profile for {user.username}")
    
    print(f"User setup complete!")
    print(f"Username: {user.username}")
    print(f"Password: sib2")
    print(f"Role: {utilisateur.role}")

if __name__ == '__main__':
    setup_user() 