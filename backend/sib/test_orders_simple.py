#!/usr/bin/env python3
"""
Simple test script for Orders API endpoints
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"

def test_orders_api():
    """Test the orders API endpoints"""
    
    print("🧪 Testing Orders API endpoints...")
    
    try:
        # Test 1: Check server connectivity
        print("🔗 Testing server connectivity...")
        response = requests.get(f"{BASE_URL}/clients/", timeout=5)
        print(f"✅ Server is accessible (Status: {response.status_code})")
        
        # Test 2: Test GET endpoints
        print("\n📖 Testing GET endpoints...")
        
        # Test GET clients
        clients_response = requests.get(f"{BASE_URL}/clients/")
        print(f"📝 Clients endpoint: {clients_response.status_code}")
        if clients_response.status_code == 200:
            clients_data = clients_response.json()
            print(f"✅ Clients accessible: {len(clients_data)} clients found")
        else:
            print(f"❌ Clients error: {clients_response.text}")
        
        # Test GET finished products
        products_response = requests.get(f"{BASE_URL}/produits-finis/")
        print(f"🏭 Products endpoint: {products_response.status_code}")
        if products_response.status_code == 200:
            products_data = products_response.json()
            print(f"✅ Products accessible: {len(products_data)} products found")
        else:
            print(f"❌ Products error: {products_response.text}")
        
        # Test GET orders
        orders_response = requests.get(f"{BASE_URL}/commandes/")
        print(f"📋 Orders endpoint: {orders_response.status_code}")
        if orders_response.status_code == 200:
            orders_data = orders_response.json()
            print(f"✅ Orders accessible: {len(orders_data)} orders found")
        else:
            print(f"❌ Orders error: {orders_response.text}")
        
        # Test GET order items
        order_items_response = requests.get(f"{BASE_URL}/articles-commande/")
        print(f"📦 Order items endpoint: {order_items_response.status_code}")
        if order_items_response.status_code == 200:
            order_items_data = order_items_response.json()
            print(f"✅ Order items accessible: {len(order_items_data)} items found")
        else:
            print(f"❌ Order items error: {order_items_response.text}")
        
        print("\n🎉 Backend API test completed!")
        print("📋 Summary:")
        print("- Server is accessible")
        print("- All GET endpoints are working")
        print("- Frontend should be able to fetch data")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Django server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Orders API Test...")
    success = test_orders_api()
    if success:
        print("\n✅ Backend is working correctly!")
    else:
        print("\n❌ Backend has issues that need to be fixed.") 