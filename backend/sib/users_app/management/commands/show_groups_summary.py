from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from users_app.models import Utilisateur

class Command(BaseCommand):
    help = 'Show a summary of all groups, their permissions, and user assignments'

    def handle(self, *args, **options):
        self.stdout.write('📊 GROUPS AND PERMISSIONS SUMMARY')
        self.stdout.write('=' * 50)
        
        # Get all groups
        groups = Group.objects.all().order_by('name')
        
        if not groups.exists():
            self.stdout.write('❌ No groups found. Run "python manage.py setup_groups" first.')
            return
        
        for group in groups:
            self.stdout.write(f'\n👥 {group.name.upper()}:')
            self.stdout.write('-' * 30)
            
            # Show permissions by app
            permissions = group.permissions.all().order_by('content_type__app_label', 'content_type__model', 'codename')
            
            if permissions.exists():
                current_app = None
                for permission in permissions:
                    app_label = permission.content_type.app_label
                    model_name = permission.content_type.model
                    action = permission.codename.replace(f'_{model_name}', '')
                    
                    if app_label != current_app:
                        current_app = app_label
                        self.stdout.write(f'\n   📁 {app_label.upper()}:')
                    
                    self.stdout.write(f'      • {model_name}: {action}')
            else:
                self.stdout.write('   ⚠️  No permissions assigned')
            
            # Show user members
            users = group.user_set.all().order_by('username')
            if users.exists():
                self.stdout.write(f'\n   👤 Members ({users.count()}):')
                for user in users:
                    try:
                        self.stdout.write(f'      • {user.username} ({user.email}) - {user.utilisateur.nom}')
                    except Utilisateur.DoesNotExist:
                        self.stdout.write(f'      • {user.username} ({user.email}) - No profile')
            else:
                self.stdout.write('\n   👤 No members')
        
        # Show users without groups
        users_without_groups = User.objects.filter(groups__isnull=True)
        if users_without_groups.exists():
            self.stdout.write(f'\n⚠️  USERS WITHOUT GROUPS ({users_without_groups.count()}):')
            self.stdout.write('-' * 30)
            for user in users_without_groups:
                try:
                    self.stdout.write(f'   • {user.username} ({user.email}) - {user.utilisateur.nom}')
                except Utilisateur.DoesNotExist:
                    self.stdout.write(f'   • {user.username} ({user.email}) - No profile')
        
        # Show users without profiles
        users_without_profiles = []
        for user in User.objects.all():
            try:
                user.utilisateur
            except Utilisateur.DoesNotExist:
                users_without_profiles.append(user)
        
        if users_without_profiles:
            self.stdout.write(f'\n⚠️  USERS WITHOUT PROFILES ({len(users_without_profiles)}):')
            self.stdout.write('-' * 30)
            for user in users_without_profiles:
                self.stdout.write(f'   • {user.username} ({user.email})')
        
        # Summary statistics
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('📈 SUMMARY STATISTICS:')
        self.stdout.write('=' * 50)
        
        total_users = User.objects.count()
        users_with_groups = User.objects.filter(groups__isnull=False).distinct().count()
        users_with_profiles = Utilisateur.objects.count()
        
        self.stdout.write(f'👥 Total users: {total_users}')
        self.stdout.write(f'✅ Users with groups: {users_with_groups}')
        self.stdout.write(f'⚠️  Users without groups: {total_users - users_with_groups}')
        self.stdout.write(f'✅ Users with profiles: {users_with_profiles}')
        self.stdout.write(f'⚠️  Users without profiles: {total_users - users_with_profiles}')
        self.stdout.write(f'🔐 Total groups: {groups.count()}')
        
        # Group distribution
        self.stdout.write('\n🎭 GROUP DISTRIBUTION:')
        self.stdout.write('-' * 20)
        
        for group in Group.objects.all():
            member_count = group.user_set.count()
            self.stdout.write(f'   • {group.name}: {member_count} users')
        
        self.stdout.write('\n✅ Summary completed!')
