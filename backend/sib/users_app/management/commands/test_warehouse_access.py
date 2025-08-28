from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users_app.models import Utilisateur, UtilisateurEntrepot
from warehouse.models import Entrepot
from users_app.permissions import (
    get_user_warehouse_permissions,
    get_user_accessible_warehouses,
    filter_queryset_by_warehouse_access
)

class Command(BaseCommand):
    help = 'Test the warehouse access system'

    def handle(self, *args, **options):
        self.stdout.write('🧪 TESTING WAREHOUSE ACCESS SYSTEM')
        self.stdout.write('=' * 50)
        
        # Get or create test warehouses
        entrepot1, created = Entrepot.objects.get_or_create(
            nom="Entrepôt Principal",
            defaults={'adresse': '123 Rue Principale', 'description': 'Entrepôt principal de test'}
        )
        entrepot2, created = Entrepot.objects.get_or_create(
            nom="Entrepôt Secondaire", 
            defaults={'adresse': '456 Rue Secondaire', 'description': 'Entrepôt secondaire de test'}
        )
        
        if created:
            self.stdout.write(f'✅ Created test warehouses: {entrepot1.nom}, {entrepot2.nom}')
        
        # Test with different users
        users_to_test = [
            ('sib', 'admin'),
            ('Salma', 'magasin'),
            ('ayoub', 'magasin'),
        ]
        
        for username, role in users_to_test:
            try:
                user = User.objects.get(username=username)
                self.stdout.write(f'\n👤 Testing user: {username} (Role: {role})')
                self.stdout.write('-' * 30)
                
                # Test accessible warehouses
                accessible_warehouses = get_user_accessible_warehouses(user)
                self.stdout.write(f'📦 Accessible warehouses: {accessible_warehouses.count()}')
                for warehouse in accessible_warehouses:
                    self.stdout.write(f'   • {warehouse.nom}')
                
                # Test permissions for each warehouse
                for warehouse in [entrepot1, entrepot2]:
                    permissions = get_user_warehouse_permissions(user, warehouse)
                    self.stdout.write(f'\n🔐 Permissions for {warehouse.nom}:')
                    self.stdout.write(f'   • Read: {permissions.get("read", False)}')
                    self.stdout.write(f'   • Write: {permissions.get("write", False)}')
                    self.stdout.write(f'   • Delete: {permissions.get("delete", False)}')
                
                # Test queryset filtering (skip if no warehouse field)
                self.stdout.write(f'\n📋 Queryset filtering test skipped (no warehouse field in models)')
                
            except User.DoesNotExist:
                self.stdout.write(f'⚠️  User {username} not found')
        
        # Test specific scenarios
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('🎯 TESTING SPECIFIC SCENARIOS')
        self.stdout.write('=' * 50)
        
        # Test user with access to all warehouses
        try:
            admin_user = User.objects.get(username='sib')
            self.stdout.write(f'\n👑 Admin user ({admin_user.username}):')
            
            # Check if admin has access to all warehouses
            accessible = get_user_accessible_warehouses(admin_user)
            self.stdout.write(f'   • Total warehouses: {Entrepot.objects.count()}')
            self.stdout.write(f'   • Accessible warehouses: {accessible.count()}')
            self.stdout.write(f'   • Has access to all: {accessible.count() == Entrepot.objects.count()}')
            
            # Test permissions for a specific warehouse
            permissions = get_user_warehouse_permissions(admin_user, entrepot1)
            self.stdout.write(f'   • Full permissions for {entrepot1.nom}: {all(permissions.values())}')
            
        except User.DoesNotExist:
            self.stdout.write('⚠️  Admin user not found')
        
        # Test warehouse-specific access
        self.stdout.write('\n🏭 WAREHOUSE-SPECIFIC ACCESS TEST:')
        
        # Create a user with specific warehouse access
        test_user, created = User.objects.get_or_create(
            username='test_warehouse_user',
            defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
        )
        
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            
            # Create Utilisateur profile
            utilisateur, created = Utilisateur.objects.get_or_create(
                user=test_user,
                defaults={'nom': 'Test User', 'acces_tous_entrepots': False}
            )
            
            # Give access only to the first warehouse
            UtilisateurEntrepot.objects.get_or_create(
                utilisateur=utilisateur,
                entrepot=entrepot1,
                defaults={
                    'peut_lire': True,
                    'peut_modifier': False,
                    'peut_supprimer': False
                }
            )
            
            self.stdout.write(f'✅ Created test user: {test_user.username}')
        
        # Test the specific access
        accessible = get_user_accessible_warehouses(test_user)
        self.stdout.write(f'   • Test user accessible warehouses: {accessible.count()}')
        for warehouse in accessible:
            self.stdout.write(f'     - {warehouse.nom}')
        
        # Test permissions
        permissions1 = get_user_warehouse_permissions(test_user, entrepot1)
        permissions2 = get_user_warehouse_permissions(test_user, entrepot2)
        
        self.stdout.write(f'   • Permissions for {entrepot1.nom}: {permissions1}')
        self.stdout.write(f'   • Permissions for {entrepot2.nom}: {permissions2}')
        
        # Clean up test user
        if created:
            test_user.delete()
            self.stdout.write('🧹 Cleaned up test user')
        
        self.stdout.write('\n✅ Warehouse access system test completed!')
        self.stdout.write('\n💡 Usage examples:')
        self.stdout.write('   1. Use @require_warehouse_access decorator for views')
        self.stdout.write('   2. Use WarehouseAccessMixin for class-based views')
        self.stdout.write('   3. Use filter_queryset_by_warehouse_access to filter data')
        self.stdout.write('   4. Use get_user_warehouse_permissions to check specific permissions')
