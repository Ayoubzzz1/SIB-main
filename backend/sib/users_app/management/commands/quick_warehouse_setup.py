from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users_app.models import Utilisateur, UtilisateurEntrepot
from warehouse.models import Entrepot

class Command(BaseCommand):
    help = 'Quick setup of warehouse access for users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='Username to set up warehouse access for'
        )
        parser.add_argument(
            '--warehouses',
            nargs='+',
            help='Warehouse names to give access to (use "all" for all warehouses)'
        )

    def handle(self, *args, **options):
        username = options['username']
        warehouses = options['warehouses']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(f'❌ User {username} not found')
            return
        
        # Get or create Utilisateur profile
        utilisateur, created = Utilisateur.objects.get_or_create(
            user=user,
            defaults={'nom': user.get_full_name() or user.username}
        )
        
        if not warehouses:
            self.stdout.write('❌ Please specify warehouses with --warehouses')
            self.stdout.write('💡 Examples:')
            self.stdout.write('   python manage.py quick_warehouse_setup --username john --warehouses "Magasin 2" "Entrepôt Principal"')
            self.stdout.write('   python manage.py quick_warehouse_setup --username admin --warehouses all')
            return
        
        if warehouses == ['all']:
            # Give access to all warehouses
            utilisateur.acces_tous_entrepots = True
            utilisateur.save()
            
            # Remove any specific warehouse access
            utilisateur.entrepots_autorises.all().delete()
            
            self.stdout.write(f'✅ User {username} now has access to ALL warehouses')
            return
        
        # Give access to specific warehouses
        utilisateur.acces_tous_entrepots = False
        utilisateur.save()
        
        # Remove existing access
        utilisateur.entrepots_autorises.all().delete()
        
        # Add access to specified warehouses
        for warehouse_name in warehouses:
            try:
                warehouse = Entrepot.objects.get(nom=warehouse_name)
                UtilisateurEntrepot.objects.create(
                    utilisateur=utilisateur,
                    entrepot=warehouse,
                    peut_lire=True,
                    peut_modifier=False,
                    peut_supprimer=False
                )
                self.stdout.write(f'✅ Added access to warehouse: {warehouse_name}')
            except Entrepot.DoesNotExist:
                self.stdout.write(f'❌ Warehouse "{warehouse_name}" not found')
        
        self.stdout.write(f'✅ User {username} now has access to specific warehouses')
        self.stdout.write('💡 They can only see stock and movements from their assigned warehouses')
        
        # Show current access
        self.show_current_access(utilisateur)
    
    def show_current_access(self, utilisateur):
        """Show the current warehouse access for the user"""
        self.stdout.write(f'\n📋 Current access for {utilisateur.user.username}:')
        
        if utilisateur.acces_tous_entrepots:
            self.stdout.write('   🔓 ALL WAREHOUSES')
        else:
            warehouses = utilisateur.entrepots_autorises.all()
            if warehouses:
                for access in warehouses:
                    perms = []
                    if access.peut_lire:
                        perms.append("Lecture")
                    if access.peut_modifier:
                        perms.append("Modification")
                    if access.peut_supprimer:
                        perms.append("Suppression")
                    
                    self.stdout.write(f'   🔒 {access.entrepot.nom}: {", ".join(perms) if perms else "Aucune permission"}')
            else:
                self.stdout.write('   ❌ NO WAREHOUSE ACCESS')
