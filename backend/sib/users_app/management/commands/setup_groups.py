from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

class Command(BaseCommand):
    help = 'Create Django groups with specific permissions for each user role'

    def handle(self, *args, **options):
        self.stdout.write('Setting up user role groups...')
        
        # Create groups for each role
        groups_data = {
            'Commerciaux': {
                'description': 'Utilisateurs avec accès commercial - Voir le stock, Créer et gérer les commandes clients, Suivre les clients',
                'permissions': [
                    # Stock permissions
                    ('inventory_app', 'matierepremiere', 'view'),
                    ('inventory_app', 'produitfini', 'view'),
                    ('inventory_app', 'produitsemifini', 'view'),
                    ('inventory_app', 'mouvementstock', 'view'),
                    ('inventory_app', 'stock', 'view'),
                    ('warehouse', 'entrepot', 'view'),
                    
                    # Sales permissions
                    ('sales_app', 'client', 'view'),
                    ('sales_app', 'client', 'add'),
                    ('sales_app', 'client', 'change'),
                    ('sales_app', 'commande', 'view'),
                    ('sales_app', 'commande', 'add'),
                    ('sales_app', 'commande', 'change'),
                    ('sales_app', 'articlecommande', 'view'),
                    ('sales_app', 'articlecommande', 'add'),
                    ('sales_app', 'articlecommande', 'change'),
                ]
            },
            'Magasiniers': {
                'description': 'Utilisateurs avec accès magasinier - Voir le stock, Voir les commandes à traiter, Confirmer et transmettre à la production',
                'permissions': [
                    # Stock permissions
                    ('inventory_app', 'matierepremiere', 'view'),
                    ('inventory_app', 'produitfini', 'view'),
                    ('inventory_app', 'produitsemifini', 'view'),
                    ('inventory_app', 'mouvementstock', 'view'),
                    ('inventory_app', 'mouvementstock', 'add'),
                    ('inventory_app', 'mouvementstock', 'change'),
                    ('inventory_app', 'stock', 'view'),
                    ('warehouse', 'entrepot', 'view'),
                    
                    # Order processing permissions
                    ('sales_app', 'commande', 'view'),
                    ('sales_app', 'commande', 'change'),  # To update order status
                    ('sales_app', 'articlecommande', 'view'),
                    ('sales_app', 'articlecommande', 'change'),  # To update line status
                    
                    # Production permissions (to confirm orders)
                    ('production_app', 'production', 'view'),
                    ('production_app', 'production', 'add'),
                ]
            },
            'Ouvriers de production': {
                'description': 'Utilisateurs avec accès production - Voir les commandes confirmées, Voir le stock matière première, Mettre à jour les statuts de production',
                'permissions': [
                    # Stock permissions (raw materials)
                    ('inventory_app', 'matierepremiere', 'view'),
                    ('inventory_app', 'mouvementstock', 'view'),
                    ('inventory_app', 'stock', 'view'),
                    ('warehouse', 'entrepot', 'view'),
                    
                    # Order permissions (confirmed orders only)
                    ('sales_app', 'commande', 'view'),
                    ('sales_app', 'articlecommande', 'view'),
                    
                    # Production permissions
                    ('production_app', 'production', 'view'),
                    ('production_app', 'production', 'add'),
                    ('production_app', 'production', 'change'),
                    ('production_app', 'matiereproduction', 'view'),
                    ('production_app', 'matiereproduction', 'add'),
                    ('production_app', 'matiereproduction', 'change'),
                    ('production_app', 'nomenclatureproduits', 'view'),
                ]
            },
            'Administrateurs': {
                'description': 'Utilisateurs avec accès complet au système',
                'permissions': [
                    # Full access to all models
                    ('inventory_app', 'matierepremiere', 'view'),
                    ('inventory_app', 'matierepremiere', 'add'),
                    ('inventory_app', 'matierepremiere', 'change'),
                    ('inventory_app', 'matierepremiere', 'delete'),
                    
                    ('inventory_app', 'produitfini', 'view'),
                    ('inventory_app', 'produitfini', 'add'),
                    ('inventory_app', 'produitfini', 'change'),
                    ('inventory_app', 'produitfini', 'delete'),
                    
                    ('inventory_app', 'produitsemifini', 'view'),
                    ('inventory_app', 'produitsemifini', 'add'),
                    ('inventory_app', 'produitsemifini', 'change'),
                    ('inventory_app', 'produitsemifini', 'delete'),
                    
                    ('inventory_app', 'mouvementstock', 'view'),
                    ('inventory_app', 'mouvementstock', 'add'),
                    ('inventory_app', 'mouvementstock', 'change'),
                    ('inventory_app', 'mouvementstock', 'delete'),
                    
                    ('inventory_app', 'stock', 'view'),
                    ('inventory_app', 'stock', 'add'),
                    ('inventory_app', 'stock', 'change'),
                    ('inventory_app', 'stock', 'delete'),
                    
                    ('sales_app', 'client', 'view'),
                    ('sales_app', 'client', 'add'),
                    ('sales_app', 'client', 'change'),
                    ('sales_app', 'client', 'delete'),
                    
                    ('sales_app', 'commande', 'view'),
                    ('sales_app', 'commande', 'add'),
                    ('sales_app', 'commande', 'change'),
                    ('sales_app', 'commande', 'delete'),
                    
                    ('sales_app', 'articlecommande', 'view'),
                    ('sales_app', 'articlecommande', 'add'),
                    ('sales_app', 'articlecommande', 'change'),
                    ('sales_app', 'articlecommande', 'delete'),
                    
                    ('sales_app', 'fournisseur', 'view'),
                    ('sales_app', 'fournisseur', 'add'),
                    ('sales_app', 'fournisseur', 'change'),
                    ('sales_app', 'fournisseur', 'delete'),
                    
                    ('production_app', 'production', 'view'),
                    ('production_app', 'production', 'add'),
                    ('production_app', 'production', 'change'),
                    ('production_app', 'production', 'delete'),
                    
                    ('production_app', 'matiereproduction', 'view'),
                    ('production_app', 'matiereproduction', 'add'),
                    ('production_app', 'matiereproduction', 'change'),
                    ('production_app', 'matiereproduction', 'delete'),
                    
                    ('production_app', 'nomenclatureproduits', 'view'),
                    ('production_app', 'nomenclatureproduits', 'add'),
                    ('production_app', 'nomenclatureproduits', 'change'),
                    ('production_app', 'nomenclatureproduits', 'delete'),
                    
                    ('warehouse', 'entrepot', 'view'),
                    ('warehouse', 'entrepot', 'add'),
                    ('warehouse', 'entrepot', 'change'),
                    ('warehouse', 'entrepot', 'delete'),
                    
                    ('users_app', 'utilisateur', 'view'),
                    ('users_app', 'utilisateur', 'add'),
                    ('users_app', 'utilisateur', 'change'),
                    ('users_app', 'utilisateur', 'delete'),
                    
                    ('users_app', 'utilisateurentrepot', 'view'),
                    ('users_app', 'utilisateurentrepot', 'add'),
                    ('users_app', 'utilisateurentrepot', 'change'),
                    ('users_app', 'utilisateurentrepot', 'delete'),
                ]
            }
        }
        
        created_groups = []
        updated_groups = []
        
        for group_name, group_data in groups_data.items():
            # Create or get the group
            group, created = Group.objects.get_or_create(
                name=group_name,
                defaults={'name': group_name}
            )
            
            if created:
                created_groups.append(group_name)
                self.stdout.write(f'✅ Created group: {group_name}')
            else:
                updated_groups.append(group_name)
                self.stdout.write(f'🔄 Updating existing group: {group_name}')
            
            # Clear existing permissions
            group.permissions.clear()
            
            # Add permissions
            permissions_added = 0
            for app_label, model_name, codename in group_data['permissions']:
                try:
                    # Get the content type
                    content_type = ContentType.objects.get(
                        app_label=app_label,
                        model=model_name
                    )
                    
                    # Get the permission
                    permission = Permission.objects.get(
                        content_type=content_type,
                        codename=f'{codename}_{model_name}'
                    )
                    
                    # Add permission to group
                    group.permissions.add(permission)
                    permissions_added += 1
                    
                except (ContentType.DoesNotExist, Permission.DoesNotExist) as e:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Permission not found: {app_label}.{model_name}.{codename} - {e}')
                    )
            
            self.stdout.write(f'   📋 Added {permissions_added} permissions to {group_name}')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📊 SETUP SUMMARY:')
        self.stdout.write('='*50)
        
        if created_groups:
            self.stdout.write(f'✅ Created {len(created_groups)} new groups: {", ".join(created_groups)}')
        
        if updated_groups:
            self.stdout.write(f'🔄 Updated {len(updated_groups)} existing groups: {", ".join(updated_groups)}')
        
        self.stdout.write('\n🎯 GROUP PERMISSIONS:')
        self.stdout.write('-'*30)
        
        for group_name, group_data in groups_data.items():
            group = Group.objects.get(name=group_name)
            self.stdout.write(f'\n👥 {group_name}:')
            self.stdout.write(f'   📝 {group_data["description"]}')
            self.stdout.write(f'   🔐 {group.permissions.count()} permissions assigned')
        
        self.stdout.write('\n✅ Group setup completed successfully!')
        self.stdout.write('\n💡 Next steps:')
        self.stdout.write('   1. Assign users to appropriate groups')
        self.stdout.write('   2. Test permissions for each role')
        self.stdout.write('   3. Customize permissions as needed')
