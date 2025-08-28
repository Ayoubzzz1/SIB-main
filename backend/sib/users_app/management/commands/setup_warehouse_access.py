from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users_app.models import Utilisateur, UtilisateurEntrepot
from warehouse.models import Entrepot

class Command(BaseCommand):
    help = 'Set up warehouse access for users - either all warehouses or specific ones'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username to set up warehouse access for'
        )
        parser.add_argument(
            '--all-warehouses',
            action='store_true',
            help='Give user access to all warehouses'
        )
        parser.add_argument(
            '--warehouses',
            nargs='+',
            help='Specific warehouse names to give access to'
        )
        parser.add_argument(
            '--list-users',
            action='store_true',
            help='List all users and their current warehouse access'
        )

    def handle(self, *args, **options):
        if options['list_users']:
            self.list_users_warehouse_access()
            return

        if not options['username']:
            self.stdout.write('❌ Please provide a username with --username')
            self.stdout.write('💡 Example: python manage.py setup_warehouse_access --username john --all-warehouses')
            return

        try:
            user = User.objects.get(username=options['username'])
        except User.DoesNotExist:
            self.stdout.write(f'❌ User {options["username"]} not found')
            return

        # Get or create Utilisateur profile
        utilisateur, created = Utilisateur.objects.get_or_create(
            user=user,
            defaults={'nom': user.get_full_name() or user.username}
        )

        if options['all_warehouses']:
            self.give_access_to_all_warehouses(utilisateur)
        elif options['warehouses']:
            self.give_access_to_specific_warehouses(utilisateur, options['warehouses'])
        else:
            self.stdout.write('❌ Please specify either --all-warehouses or --warehouses')
            self.stdout.write('💡 Example: python manage.py setup_warehouse_access --username john --warehouses Entrepot1 Entrepot2')

    def give_access_to_all_warehouses(self, utilisateur):
        """Give user access to all warehouses"""
        utilisateur.acces_tous_entrepots = True
        utilisateur.save()
        
        # Remove any specific warehouse access since user now has access to all
        utilisateur.entrepots_autorises.all().delete()
        
        self.stdout.write(f'✅ User {utilisateur.user.username} now has access to ALL warehouses')
        self.stdout.write('💡 This means they can see stock and movements from all warehouses')

    def give_access_to_specific_warehouses(self, utilisateur, warehouse_names):
        """Give user access to specific warehouses"""
        utilisateur.acces_tous_entrepots = False
        utilisateur.save()
        
        # Remove existing access
        utilisateur.entrepots_autorises.all().delete()
        
        # Add access to specified warehouses
        for warehouse_name in warehouse_names:
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
        
        self.stdout.write(f'✅ User {utilisateur.user.username} now has access to specific warehouses')
        self.stdout.write('💡 They can only see stock and movements from their assigned warehouses')

    def list_users_warehouse_access(self):
        """List all users and their warehouse access"""
        self.stdout.write('👥 USERS AND WAREHOUSE ACCESS')
        self.stdout.write('=' * 50)
        
        for user in User.objects.all():
            try:
                utilisateur = user.utilisateur
                if utilisateur.acces_tous_entrepots:
                    access_info = "🔓 ALL WAREHOUSES"
                else:
                    warehouses = utilisateur.entrepots_autorises.all()
                    if warehouses:
                        warehouse_names = [w.entrepot.nom for w in warehouses]
                        access_info = f"🔒 {len(warehouses)} warehouse(s): {', '.join(warehouse_names)}"
                    else:
                        access_info = "❌ NO WAREHOUSE ACCESS"
                
                self.stdout.write(f'{user.username:15} | {access_info}')
                
            except Utilisateur.DoesNotExist:
                self.stdout.write(f'{user.username:15} | ❌ NO PROFILE')
        
        self.stdout.write('\n💡 To give access to all warehouses: --all-warehouses')
        self.stdout.write('💡 To give access to specific warehouses: --warehouses Entrepot1 Entrepot2')
