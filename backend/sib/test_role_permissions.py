#!/usr/bin/env python
"""
Role Permission Test Script
Tests all role permissions according to the specified requirements
"""

import os
import sys
import django
import requests
import json
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sib.settings')
django.setup()

def test_role_permissions():
    """Test all role permissions"""
    print("🔐 Testing Role Permissions...")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test users for each role
    test_users = {
        'commercial': {'username': 'commercial_test', 'password': 'testpass123'},
        'magasin': {'username': 'magasin_test', 'password': 'testpass123'},
        'production': {'username': 'production_test', 'password': 'testpass123'},
        'admin': {'username': 'sib2', 'password': 'sib2'}
    }
    
    # Define expected permissions for each role
    expected_permissions = {
        'commercial': {
            'can_view_stock': True,
            'can_manage_orders': True,
            'can_manage_clients': True,
            'can_manage_suppliers': True,
            'can_manage_inventory': False,
            'can_manage_production': False,
            'can_manage_users': False,
            'can_view_logs': False
        },
        'magasin': {
            'can_view_stock': True,
            'can_manage_orders': False,
            'can_view_orders': True,
            'can_manage_inventory': True,
            'can_manage_stock': True,
            'can_manage_warehouses': True,
            'can_manage_production': False,
            'can_manage_users': False,
            'can_view_logs': False
        },
        'production': {
            'can_view_stock': True,
            'can_view_orders': True,
            'can_manage_production': True,
            'can_manage_inventory': False,
            'can_manage_users': False,
            'can_view_logs': False
        },
        'admin': {
            'can_view_stock': True,
            'can_manage_orders': True,
            'can_manage_clients': True,
            'can_manage_suppliers': True,
            'can_manage_inventory': True,
            'can_manage_stock': True,
            'can_manage_warehouses': True,
            'can_manage_production': True,
            'can_manage_users': True,
            'can_view_logs': True
        }
    }
    
    # Test endpoints for each permission
    test_endpoints = {
        'can_view_stock': [
            ('GET', '/api/matieres-premieres/', 'Raw Materials'),
            ('GET', '/api/produits-semi-finis/', 'Semi-finished Products'),
            ('GET', '/api/produits-finis/', 'Finished Products'),
            ('GET', '/api/stock/', 'Stock'),
        ],
        'can_manage_orders': [
            ('GET', '/api/commandes/', 'Orders'),
            ('POST', '/api/commandes/', 'Create Order'),
        ],
        'can_view_orders': [
            ('GET', '/api/commandes/', 'Orders'),
        ],
        'can_manage_clients': [
            ('GET', '/api/clients/', 'Clients'),
            ('POST', '/api/clients/', 'Create Client'),
        ],
        'can_manage_suppliers': [
            ('GET', '/api/fournisseurs/', 'Suppliers'),
            ('POST', '/api/fournisseurs/', 'Create Supplier'),
        ],
        'can_manage_inventory': [
            ('POST', '/api/matieres-premieres/', 'Create Material'),
            ('PUT', '/api/matieres-premieres/1/', 'Update Material'),
        ],
        'can_manage_stock': [
            ('GET', '/api/mouvements-stock/', 'Stock Movements'),
            ('POST', '/api/mouvements-stock/', 'Create Stock Movement'),
        ],
        'can_manage_warehouses': [
            ('GET', '/api/entrepots/', 'Warehouses'),
            ('POST', '/api/entrepots/', 'Create Warehouse'),
        ],
        'can_manage_production': [
            ('GET', '/api/production/', 'Production'),
            ('POST', '/api/production/', 'Create Production Order'),
        ],
        'can_manage_users': [
            ('GET', '/api/users/utilisateurs/', 'Users'),
            ('POST', '/api/users/utilisateurs/', 'Create User'),
        ],
        'can_view_logs': [
            ('GET', '/api/historique-activites/', 'Activity Logs'),
        ]
    }
    
    results = {}
    
    for role, user_creds in test_users.items():
        print(f"\n👤 Testing {role.upper()} role...")
        print("-" * 40)
        
        # Authenticate as this role
        try:
            auth_response = requests.post(f"{base_url}/token/", json=user_creds)
            if auth_response.status_code != 200:
                print(f"❌ Failed to authenticate as {role}: {auth_response.status_code}")
                continue
                
            token = auth_response.json().get('token')
            headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
            print(f"✅ Authenticated as {role}")
            
        except Exception as e:
            print(f"❌ Authentication error for {role}: {e}")
            continue
        
        role_results = {}
        
        # Test each permission
        for permission, expected in expected_permissions[role].items():
            if permission not in test_endpoints:
                continue
                
            print(f"\n  🔍 Testing {permission}...")
            permission_results = []
            
            for method, endpoint, name in test_endpoints[permission]:
                try:
                    if method == 'GET':
                        response = requests.get(f"{base_url}{endpoint}", headers=headers)
                    elif method == 'POST':
                        # Create test data
                        test_data = create_test_data(endpoint, role)
                        response = requests.post(f"{base_url}{endpoint}", json=test_data, headers=headers)
                    elif method == 'PUT':
                        response = requests.put(f"{base_url}{endpoint}", json={}, headers=headers)
                    
                    if response.status_code == 200 or response.status_code == 201:
                        result = "✅ ALLOWED"
                        permission_results.append(True)
                    elif response.status_code == 403:
                        result = "❌ DENIED"
                        permission_results.append(False)
                    else:
                        result = f"⚠️  {response.status_code}"
                        permission_results.append(False)
                        
                    print(f"    {method} {endpoint}: {result}")
                    
                except Exception as e:
                    print(f"    {method} {endpoint}: ❌ ERROR - {e}")
                    permission_results.append(False)
            
            # Determine if permission is working as expected
            if permission_results:
                actual_result = any(permission_results)  # If any request succeeded
                expected_result = expected
                
                if actual_result == expected_result:
                    status = "✅ PASS"
                else:
                    status = "❌ FAIL"
                    
                role_results[permission] = {
                    'expected': expected_result,
                    'actual': actual_result,
                    'status': status
                }
                
                print(f"  {permission}: {status} (Expected: {expected_result}, Actual: {actual_result})")
        
        results[role] = role_results
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 ROLE PERMISSION TEST SUMMARY")
    print("=" * 60)
    
    for role, role_results in results.items():
        print(f"\n{role.upper()}:")
        passed = 0
        total = len(role_results)
        
        for permission, result in role_results.items():
            print(f"  {permission}: {result['status']}")
            if result['status'] == "✅ PASS":
                passed += 1
        
        print(f"  Score: {passed}/{total} ({passed/total*100:.1f}%)")
    
    return results

def create_test_data(endpoint, role):
    """Create test data for POST requests"""
    timestamp = int(time.time())
    
    if 'utilisateurs' in endpoint:
        return {
            "nom": f"Test User {timestamp}",
            "user": {
                "username": f"testuser_{timestamp}",
                "email": f"test_{timestamp}@example.com",
                "password": "testpass123"
            },
            "role": "commercial"
        }
    elif 'matieres-premieres' in endpoint:
        return {
            "nom": f"Test Material {timestamp}",
            "code_reference": f"TEST{timestamp}",
            "unite": "kg",
            "niveau_min_stock": 10.0
        }
    elif 'clients' in endpoint:
        return {
            "nom": f"Test Client {timestamp}",
            "email": f"client_{timestamp}@example.com",
            "telephone": "123456789"
        }
    elif 'fournisseurs' in endpoint:
        return {
            "nom": f"Test Supplier {timestamp}",
            "email": f"supplier_{timestamp}@example.com",
            "telephone": "123456789"
        }
    elif 'entrepots' in endpoint:
        return {
            "nom": f"Test Warehouse {timestamp}",
            "adresse": f"Address {timestamp}",
            "capacite": 1000.0
        }
    elif 'production' in endpoint:
        return {
            "quantite_prevue": 10.0,
            "date_debut": "2024-01-01",
            "statut": "planifiee"
        }
    else:
        return {}

def main():
    """Run the role permission tests"""
    print("🚀 Starting Role Permission Tests...")
    print("=" * 60)
    
    # Test role permissions
    results = test_role_permissions()
    
    print("\n✨ Role permission tests completed!")

if __name__ == "__main__":
    main() 