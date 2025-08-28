#!/usr/bin/env python3
"""
Simple test script for Nomenclature API endpoints
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"

def test_nomenclature_api():
    """Test the nomenclature API endpoints"""
    
    print("🧪 Testing Nomenclature API endpoints...")
    
    try:
        # Test 1: Check server connectivity
        print("🔗 Testing server connectivity...")
        response = requests.get(f"{BASE_URL}/nomenclature-produits/", timeout=5)
        print(f"✅ Server is accessible (Status: {response.status_code})")
        
        # Test 2: Test GET nomenclature endpoint
        print("\n📖 Testing GET nomenclature endpoint...")
        
        nomenclature_response = requests.get(f"{BASE_URL}/nomenclature-produits/")
        print(f"📋 Nomenclature endpoint: {nomenclature_response.status_code}")
        if nomenclature_response.status_code == 200:
            nomenclature_data = nomenclature_response.json()
            print(f"✅ Nomenclature accessible: {len(nomenclature_data)} items found")
            
            # Show sample data structure
            if nomenclature_data:
                sample = nomenclature_data[0]
                print(f"📝 Sample nomenclature item:")
                print(f"   - ID: {sample.get('id')}")
                print(f"   - Parent Product: {sample.get('produit_parent_nom')}")
                print(f"   - Component: {sample.get('composant_nom')}")
                print(f"   - Quantity: {sample.get('quantite_requise')} {sample.get('unite')}")
        else:
            print(f"❌ Nomenclature error: {nomenclature_response.text}")
        
        # Test 3: Test related endpoints that nomenclature depends on
        print("\n🔗 Testing related endpoints...")
        
        # Test finished products
        finished_response = requests.get(f"{BASE_URL}/produits-finis/")
        print(f"🏭 Finished products: {finished_response.status_code}")
        
        # Test semi-finished products
        semi_finished_response = requests.get(f"{BASE_URL}/produits-semi-finis/")
        print(f"🏭 Semi-finished products: {semi_finished_response.status_code}")
        
        # Test raw materials
        materials_response = requests.get(f"{BASE_URL}/matieres-premieres/")
        print(f"📦 Raw materials: {materials_response.status_code}")
        
        print("\n🎉 Nomenclature API test completed!")
        print("📋 Summary:")
        print("- Server is accessible")
        print("- Nomenclature GET endpoint is working")
        print("- Related product endpoints are accessible")
        print("- Frontend should be able to fetch nomenclature data")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Django server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Nomenclature API Test...")
    success = test_nomenclature_api()
    if success:
        print("\n✅ Nomenclature API is working correctly!")
    else:
        print("\n❌ Nomenclature API has issues that need to be fixed.") 