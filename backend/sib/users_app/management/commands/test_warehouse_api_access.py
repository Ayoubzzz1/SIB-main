from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from users_app.models import Utilisateur, UtilisateurEntrepot
from warehouse.models import Entrepot
from inventory_app.models import Stock, MouvementStock, MatierePremiere
from users_app.permissions import get_user_accessible_warehouses, get_user_warehouse_permissions

class Command(BaseCommand):
    help = 'Test warehouse access filtering in API endpoints'

    def handle(self, *args, **options):
        self.stdout.write('🧪 TESTING WAREHOUSE API ACCESS')
        self.stdout.write('=' * 50)
        
        # Create test client
        client = Client()
        
        # Test with different users
        users_to_test = [
            ('sib', 'admin'),
            ('Salma', 'magasin'),
            ('ayoub', 'magasin'),
        ]
        
        for username, role in users_to_test:
            try:
                user = User.objects.get(username=username)
                self.stdout.write(f'\n👤 Testing API access for user: {username} (Role: {role})')
                self.stdout.write('-' * 40)
                
                # Login the user
                client.force_login(user)
                
                # Test accessible warehouses
                accessible_warehouses = get_user_accessible_warehouses(user)
                self.stdout.write(f'📦 Accessible warehouses: {accessible_warehouses.count()}')
                for warehouse in accessible_warehouses:
                    self.stdout.write(f'   • {warehouse.nom}')
                
                # Test stock API endpoint
                self.test_stock_api(client, user, accessible_warehouses)
                
                # Test warehouse API endpoint
                self.test_warehouse_api(client, user, accessible_warehouses)
                
            except User.DoesNotExist:
                self.stdout.write(f'⚠️  User {username} not found')
        
        self.stdout.write('\n✅ Warehouse API access test completed!')

    def test_stock_api(self, client, user, accessible_warehouses):
        """Test stock API endpoint filtering"""
        self.stdout.write('\n📋 Testing Stock API:')
        
        # Get all stock in the system
        all_stock = Stock.objects.all()
        self.stdout.write(f'   • Total stock in system: {all_stock.count()}')
        
        # Get stock accessible to user
        accessible_stock = Stock.objects.filter(entrepot__in=accessible_warehouses)
        self.stdout.write(f'   • Stock accessible to user: {accessible_stock.count()}')
        
        # Test API endpoint
        try:
            response = client.get('/api/stock/')
            if response.status_code == 200:
                data = response.json()
                api_stock_count = len(data.get('results', data)) if isinstance(data, dict) else len(data)
                self.stdout.write(f'   • API returned stock count: {api_stock_count}')
                
                if api_stock_count == accessible_stock.count():
                    self.stdout.write('   ✅ API filtering working correctly!')
                else:
                    self.stdout.write('   ❌ API filtering not working correctly!')
            else:
                self.stdout.write(f'   ❌ API request failed: {response.status_code}')
        except Exception as e:
            self.stdout.write(f'   ❌ API test error: {e}')

    def test_warehouse_api(self, client, user, accessible_warehouses):
        """Test warehouse API endpoint filtering"""
        self.stdout.write('\n🏭 Testing Warehouse API:')
        
        # Get all warehouses in the system
        all_warehouses = Entrepot.objects.all()
        self.stdout.write(f'   • Total warehouses in system: {all_warehouses.count()}')
        self.stdout.write(f'   • Warehouses accessible to user: {accessible_warehouses.count()}')
        
        # Test API endpoint
        try:
            response = client.get('/api/entrepots/')
            if response.status_code == 200:
                data = response.json()
                api_warehouse_count = len(data.get('results', data)) if isinstance(data, dict) else len(data)
                self.stdout.write(f'   • API returned warehouse count: {api_warehouse_count}')
                
                if api_warehouse_count == accessible_warehouses.count():
                    self.stdout.write('   ✅ API filtering working correctly!')
                else:
                    self.stdout.write('   ❌ API filtering not working correctly!')
            else:
                self.stdout.write(f'   ❌ API request failed: {response.status_code}')
        except Exception as e:
            self.stdout.write(f'   ❌ API test error: {e}')

    def test_stock_movements_api(self, client, user, accessible_warehouses):
        """Test stock movements API endpoint filtering"""
        self.stdout.write('\n📦 Testing Stock Movements API:')
        
        # Get all movements in the system
        all_movements = MouvementStock.objects.all()
        self.stdout.write(f'   • Total movements in system: {all_movements.count()}')
        
        # Get movements accessible to user
        accessible_movements = MouvementStock.objects.filter(entrepot__in=accessible_warehouses)
        self.stdout.write(f'   • Movements accessible to user: {accessible_movements.count()}')
        
        # Test API endpoint
        try:
            response = client.get('/api/mouvements-stock/')
            if response.status_code == 200:
                data = response.json()
                api_movements_count = len(data.get('results', data)) if isinstance(data, dict) else len(data)
                self.stdout.write(f'   • API returned movements count: {api_movements_count}')
                
                if api_movements_count == accessible_movements.count():
                    self.stdout.write('   ✅ API filtering working correctly!')
                else:
                    self.stdout.write('   ❌ API filtering not working correctly!')
            else:
                self.stdout.write(f'   ❌ API request failed: {response.status_code}')
        except Exception as e:
            self.stdout.write(f'   ❌ API test error: {e}')

