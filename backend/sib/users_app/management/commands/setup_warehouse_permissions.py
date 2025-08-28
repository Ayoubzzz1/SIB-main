from django.core.management.base import BaseCommand
from users_app.permissions import create_warehouse_permissions, assign_warehouse_permissions_to_groups

class Command(BaseCommand):
    help = 'Set up warehouse permissions and assign them to groups'

    def handle(self, *args, **options):
        self.stdout.write('Setting up warehouse permissions...')
        
        # Create warehouse permissions
        created_permissions = create_warehouse_permissions()
        
        if created_permissions:
            self.stdout.write(f'✅ Created {len(created_permissions)} warehouse permissions:')
            for permission in created_permissions:
                self.stdout.write(f'   • {permission.name} ({permission.codename})')
        else:
            self.stdout.write('ℹ️  Warehouse permissions already exist')
        
        # Assign permissions to groups
        try:
            assign_warehouse_permissions_to_groups()
            self.stdout.write('✅ Assigned warehouse permissions to groups')
        except Exception as e:
            self.stdout.write(f'❌ Error assigning permissions to groups: {e}')
            self.stdout.write('Make sure groups exist by running "python manage.py setup_groups" first')
            return
        
        self.stdout.write('\n🎯 Warehouse permissions setup:')
        self.stdout.write('   • Commerciaux: Read access to all warehouses')
        self.stdout.write('   • Magasiniers: Read and write access to all warehouses')
        self.stdout.write('   • Ouvriers de production: Read access to all warehouses')
        self.stdout.write('   • Administrateurs: Full access to all warehouses')
        
        self.stdout.write('\n✅ Warehouse permissions setup completed!')
        self.stdout.write('\n💡 Next steps:')
        self.stdout.write('   1. Use the permission functions in your views')
        self.stdout.write('   2. Use @require_warehouse_access decorator for warehouse-specific views')
        self.stdout.write('   3. Use WarehouseAccessMixin for class-based views')
        self.stdout.write('   4. Use filter_queryset_by_warehouse_access to filter data')

