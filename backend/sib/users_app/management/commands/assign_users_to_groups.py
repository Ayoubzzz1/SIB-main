from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from users_app.models import Utilisateur

class Command(BaseCommand):
    help = 'Assign users to Django groups based on their role'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reassignment of users to groups (clear existing group memberships)',
        )

    def handle(self, *args, **options):
        self.stdout.write('Assigning users to groups...')
        
        # Note: Since we removed the role field, users will need to be assigned to groups manually
        # This command now just shows the current group assignments
        self.stdout.write('⚠️  Role field has been removed. Users must be assigned to groups manually in the admin.')
        self.stdout.write('💡 Use the Django admin interface to assign users to appropriate groups.')
        
        # Get all groups
        groups = {group.name: group for group in Group.objects.all()}
        
        if not groups:
            self.stdout.write('❌ No groups found. Run "python manage.py setup_groups" first.')
            return
        
        # Get all groups
        groups = {group.name: group for group in Group.objects.all()}
        
        # Show available groups
        self.stdout.write(f'\n📋 Available groups: {", ".join(groups.keys())}')
        
        # Get all users with Utilisateur profiles
        users_with_profiles = []
        users_without_profiles = []
        
        for user in User.objects.all():
            try:
                utilisateur = user.utilisateur
                users_with_profiles.append((user, utilisateur))
            except Utilisateur.DoesNotExist:
                users_without_profiles.append(user)
        
        self.stdout.write(f'📊 Found {len(users_with_profiles)} users with profiles')
        self.stdout.write(f'⚠️  Found {len(users_without_profiles)} users without profiles')
        
        if users_without_profiles:
            self.stdout.write('Users without profiles:')
            for user in users_without_profiles:
                self.stdout.write(f'   - {user.username} ({user.email})')
        
        # Show current group assignments
        self.stdout.write('\n📊 CURRENT GROUP ASSIGNMENTS:')
        self.stdout.write('=' * 50)
        
        for user in User.objects.all():
            try:
                utilisateur = user.utilisateur
                groups_list = list(user.groups.all())
                group_names = ", ".join([g.name for g in groups_list]) if groups_list else "Aucun groupe"
                self.stdout.write(f'👤 {user.username} ({utilisateur.nom}): {group_names}')
            except Utilisateur.DoesNotExist:
                groups_list = list(user.groups.all())
                group_names = ", ".join([g.name for g in groups_list]) if groups_list else "Aucun groupe"
                self.stdout.write(f'👤 {user.username} (Pas de profil): {group_names}')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📊 SUMMARY:')
        self.stdout.write('='*50)
        
        self.stdout.write(f'\n💡 To assign users to groups:')
        self.stdout.write('   1. Go to Django Admin → Users')
        self.stdout.write('   2. Edit a user')
        self.stdout.write('   3. In the "Rôle et permissions" section, select the appropriate groups')
        self.stdout.write('   4. Save the user')
        
        self.stdout.write(f'\n🎯 Available groups and their purposes:')
        self.stdout.write('   • Commerciaux: Voir le stock, Créer et gérer les commandes clients, Suivre les clients')
        self.stdout.write('   • Magasiniers: Voir le stock, Voir les commandes à traiter, Confirmer et transmettre à la production')
        self.stdout.write('   • Ouvriers de production: Voir les commandes confirmées, Voir le stock matière première, Mettre à jour les statuts de production')
        self.stdout.write('   • Administrateurs: Accès complet au système')
        
        # Group statistics
        self.stdout.write('\n📈 GROUP STATISTICS:')
        self.stdout.write('-'*30)
        
        for group_name, group in groups.items():
            member_count = group.user_set.count()
            self.stdout.write(f'👥 {group_name}: {member_count} members')
        
        self.stdout.write('\n✅ Group assignment summary completed!')
        
        if users_without_profiles:
            self.stdout.write('\n💡 Recommendations:')
            self.stdout.write('   1. Create Utilisateur profiles for users without them')
            self.stdout.write('   2. Assign users to appropriate groups in the admin interface')
            self.stdout.write('   3. Or run "python manage.py fix_users" to create profiles automatically')
