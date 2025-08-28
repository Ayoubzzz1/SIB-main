#!/usr/bin/env python
import os
import sys
import django
import requests
import json
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sib.settings')
django.setup()

from django.contrib.auth.models import User
from users_app.models import Utilisateur

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing API Endpoints...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/admin/")
        print(f"✅ Server is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the server first.")
        return False
    
    # Test 2: Authentication
    print("\n🔐 Testing Authentication...")
    auth_data = {
        "username": "sib2",
        "password": "sib2"
    }
    
    try:
        response = requests.post(f"{base_url}/token/", json=auth_data)
        if response.status_code == 200:
            token = response.json().get('token')
            print(f"✅ Authentication successful. Token: {token[:20]}...")
            headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Test 3: Test all API endpoints
    endpoints = [
        ("GET", "/api/users/utilisateurs/", "Users"),
        ("GET", "/api/matieres-premieres/", "Raw Materials"),
        ("GET", "/api/produits-semi-finis/", "Semi-finished Products"),
        ("GET", "/api/produits-finis/", "Finished Products"),
        ("GET", "/api/stock/", "Stock"),
        ("GET", "/api/mouvements-stock/", "Stock Movements"),
        ("GET", "/api/clients/", "Clients"),
        ("GET", "/api/fournisseurs/", "Suppliers"),
        ("GET", "/api/commandes/", "Orders"),
        ("GET", "/api/production/", "Production"),
        ("GET", "/api/messages/", "Messages"),
        ("GET", "/api/historique-activites/", "Activity Logs"),
        ("GET", "/api/entrepots/", "Warehouses"),
    ]
    
    print("\n📊 Testing API Endpoints...")
    for method, endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('results', data)) if isinstance(data, dict) else len(data)
                print(f"✅ {name}: {count} items (Status: {response.status_code})")
            elif response.status_code == 403:
                print(f"⚠️  {name}: Permission denied (Status: {response.status_code})")
            else:
                print(f"❌ {name}: Failed (Status: {response.status_code})")
                print(f"   Response: {response.text[:100]}...")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
    
    # Test 4: Test POST endpoints
    print("\n📝 Testing POST Endpoints...")
    
    # Generate unique timestamp for test data
    timestamp = int(time.time())
    
    # Test creating a user
    user_data = {
        "nom": f"Test User {timestamp}",
        "user": {
            "username": f"testuser{timestamp}",
            "email": f"test{timestamp}@example.com",
            "password": "testpass123"
        },
        "role": "commercial"
    }
    
    try:
        response = requests.post(f"{base_url}/api/users/utilisateurs/", 
                               json=user_data, headers=headers)
        if response.status_code in [201, 200]:
            print("✅ User creation: Success")
        else:
            print(f"❌ User creation: Failed (Status: {response.status_code})")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ User creation: Error - {e}")
    
    # Test creating a material
    material_data = {
        "nom": f"Test Material {timestamp}",
        "code_reference": f"TEST{timestamp}",
        "unite": "kg",
        "niveau_min_stock": 10.0
    }
    
    try:
        response = requests.post(f"{base_url}/api/matieres-premieres/", 
                               json=material_data, headers=headers)
        if response.status_code in [201, 200]:
            print("✅ Material creation: Success")
        else:
            print(f"❌ Material creation: Failed (Status: {response.status_code})")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Material creation: Error - {e}")
    
    print("\n🎉 API Testing Complete!")
    return True

def test_database():
    """Test database connectivity and data"""
    print("\n🗄️  Testing Database...")
    print("=" * 50)
    
    try:
        # Test users
        users_count = User.objects.count()
        print(f"✅ Users in database: {users_count}")
        
        # Test utilisateurs
        utilisateurs_count = Utilisateur.objects.count()
        print(f"✅ Utilisateurs in database: {utilisateurs_count}")
        
        # Test other models
        from inventory_app.models import MatierePremiere, ProduitSemiFini, ProduitFini
        from sales_app.models import Client, Fournisseur
        from logs_app.models import HistoriqueActivite
        
        matieres_count = MatierePremiere.objects.count()
        print(f"✅ Raw Materials in database: {matieres_count}")
        
        produits_semi_count = ProduitSemiFini.objects.count()
        print(f"✅ Semi-finished Products in database: {produits_semi_count}")
        
        produits_fini_count = ProduitFini.objects.count()
        print(f"✅ Finished Products in database: {produits_fini_count}")
        
        clients_count = Client.objects.count()
        print(f"✅ Clients in database: {clients_count}")
        
        fournisseurs_count = Fournisseur.objects.count()
        print(f"✅ Suppliers in database: {fournisseurs_count}")
        
        logs_count = HistoriqueActivite.objects.count()
        print(f"✅ Activity Logs in database: {logs_count}")
        
    except Exception as e:
        print(f"❌ Database test error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Comprehensive API Test...")
    print("=" * 50)
    
    # Test database first
    test_database()
    
    # Test API endpoints
    test_api_endpoints()
    
    print("\n✨ All tests completed!") 