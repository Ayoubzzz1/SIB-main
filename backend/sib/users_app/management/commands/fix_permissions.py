from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from users_app.models import Utilisateur

class Command(BaseCommand):
    help = 'Fix all permission issues by setting up groups and assigning users properly'

    def add_arguments(self, parser):
        parser.add_argument(
            '--setup-groups',
            action='store_true',
            help='Set up Django groups with proper permissions'
        )
        parser.add_argument(
            '--assign-users',
            action='store_true',
            help='Assign users to appropriate groups'
        )
        parser.add_argument(
            '--fix-all',
            action='store_true',
            help='Run all fixes (setup groups, assign users, etc.)'
        )

    def handle(self, *args, **options):
        if options['fix_all']:
            self.setup_groups()
            self.assign_users_to_groups()
            self.verify_permissions()
            return

        if options['setup_groups']:
            self.setup_groups()
            return

        if options['assign_users']:
            self.assign_users_to_groups()
            return

        # Show help if no valid options provided
        self.stdout.write(self.style.ERROR('Please provide valid options. Use --help for more information.'))
        self.stdout.write('\nExamples:')
        self.stdout.write('  python manage.py fix_permissions --fix-all')
        self.stdout.write('  python manage.py fix_permissions --setup-groups')
        self.stdout.write('  python manage.py fix_permissions --assign-users')

    def setup_groups(self):
        """Set up Django groups with proper permissions"""
        self.stdout.write('🔧 SETTING UP DJANGO GROUPS...')
        self.stdout.write('=' * 40)
        
        # First, run the setup_groups command
        from django.core.management import call_command
        try:
            call_command('setup_groups')
            self.stdout.write(self.style.SUCCESS('✅ Groups setup completed!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error setting up groups: {e}'))
            return

    def assign_users_to_groups(self):
        """Assign users to appropriate groups"""
        self.stdout.write('\n👥 ASSIGNING USERS TO GROUPS...')
        self.stdout.write('=' * 40)
        
        # Get all groups
        try:
            groups = {group.name: group for group in Group.objects.all()}
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error getting groups: {e}'))
            return

        if not groups:
            self.stdout.write(self.style.ERROR('❌ No groups found. Run --setup-groups first.'))
            return

        # Get default group
        default_group = groups.get('Commerciaux')
        if not default_group:
            self.stdout.write(self.style.ERROR('❌ Default group "Commerciaux" not found.'))
            return

        # Assign users to groups
        users_assigned = 0
        for user in User.objects.all():
            if not user.groups.exists() and not user.is_superuser:
                # Assign to default group
                user.groups.add(default_group)
                users_assigned += 1
                self.stdout.write(f'   ✅ Assigned {user.username} to {default_group.name}')

        if users_assigned == 0:
            self.stdout.write(self.style.SUCCESS('✅ All users already have groups assigned!'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Successfully assigned {users_assigned} users to groups!')
            )

    def verify_permissions(self):
        """Verify that permissions are working correctly"""
        self.stdout.write('\n🔍 VERIFYING PERMISSIONS...')
        self.stdout.write('=' * 40)
        
        # Check if groups exist
        groups = Group.objects.all()
        if not groups.exists():
            self.stdout.write(self.style.ERROR('❌ No groups found!'))
            return

        self.stdout.write(f'✅ Found {groups.count()} groups:')
        for group in groups:
            permission_count = group.permissions.count()
            user_count = group.user_set.count()
            self.stdout.write(f'   • {group.name}: {permission_count} permissions, {user_count} users')

        # Check users without groups
        users_without_groups = User.objects.filter(groups__isnull=True, is_superuser=False)
        if users_without_groups.exists():
            self.stdout.write(self.style.WARNING(f'\n⚠️  Found {users_without_groups.count()} users without groups:'))
            for user in users_without_groups:
                self.stdout.write(f'   • {user.username}')
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ All users have groups assigned!'))

        # Check users without profiles
        users_without_profiles = []
        for user in User.objects.all():
            try:
                user.utilisateur
            except Utilisateur.DoesNotExist:
                users_without_profiles.append(user)

        if users_without_profiles:
            self.stdout.write(self.style.WARNING(f'\n⚠️  Found {len(users_without_profiles)} users without profiles:'))
            for user in users_without_profiles:
                self.stdout.write(f'   • {user.username}')
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ All users have profiles!'))

        self.stdout.write('\n🎯 PERMISSION SYSTEM STATUS:')
        self.stdout.write('=' * 30)
        
        # Test permission classes
        from users_app.permissions import HasGroupPermission
        
        # Test each group
        for group in groups:
            test_user = group.user_set.first()
            if test_user:
                self.stdout.write(f'\n👤 Testing permissions for group "{group.name}":')
                
                # Test basic group permission
                permission = HasGroupPermission()
                permission.required_groups = [group.name]
                
                # Create a mock request
                from django.test import RequestFactory
                factory = RequestFactory()
                request = factory.get('/')
                request.user = test_user
                
                if permission.has_permission(request, None):
                    self.stdout.write(f'   ✅ Group permissions working for {group.name}')
                else:
                    self.stdout.write(f'   ❌ Group permissions not working for {group.name}')

        self.stdout.write('\n✅ Permission verification completed!')
