from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from users_app.models import Utilisateur

class Command(BaseCommand):
    help = 'Assign users to Django groups and fix permission issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Specific username to assign to a group'
        )
        parser.add_argument(
            '--group',
            type=str,
            choices=['Commerciaux', 'Magasiniers', 'Ouvriers de production', 'Administrateurs'],
            help='Group to assign the user to'
        )
        parser.add_argument(
            '--list-users',
            action='store_true',
            help='List all users and their current groups'
        )
        parser.add_argument(
            '--fix-all',
            action='store_true',
            help='Assign default groups to users without any groups'
        )

    def handle(self, *args, **options):
        if options['list_users']:
            self.list_users_and_groups()
            return

        if options['fix_all']:
            self.fix_all_users()
            return

        if options['username'] and options['group']:
            self.assign_user_to_group(options['username'], options['group'])
            return

        # Show help if no valid options provided
        self.stdout.write(self.style.ERROR('Please provide valid options. Use --help for more information.'))
        self.stdout.write('\nExamples:')
        self.stdout.write('  python manage.py assign_users_to_groups --list-users')
        self.stdout.write('  python manage.py assign_users_to_groups --fix-all')
        self.stdout.write('  python manage.py assign_users_to_groups --username john --group Commerciaux')

    def list_users_and_groups(self):
        """List all users and their current groups"""
        self.stdout.write('👥 USERS AND THEIR GROUPS:')
        self.stdout.write('=' * 50)
        
        for user in User.objects.all().prefetch_related('groups'):
            groups = list(user.groups.values_list('name', flat=True))
            group_str = ', '.join(groups) if groups else '❌ No groups'
            
            try:
                profile = user.utilisateur
                profile_info = f"Profile: {profile.nom}"
            except Utilisateur.DoesNotExist:
                profile_info = "❌ No profile"
            
            self.stdout.write(f'\n👤 {user.username} ({user.email})')
            self.stdout.write(f'   📋 {profile_info}')
            self.stdout.write(f'   🔐 Groups: {group_str}')
            self.stdout.write(f'   👑 Superuser: {"✅" if user.is_superuser else "❌"}')
            self.stdout.write(f'   🛠️  Staff: {"✅" if user.is_staff else "❌"}')

    def assign_user_to_group(self, username, group_name):
        """Assign a specific user to a specific group"""
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ User "{username}" not found'))
            return

        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Group "{group_name}" not found'))
            self.stdout.write('Available groups:')
            for g in Group.objects.all():
                self.stdout.write(f'   • {g.name}')
            return

        # Clear existing groups and assign to new group
        user.groups.clear()
        user.groups.add(group)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Successfully assigned user "{username}" to group "{group_name}"')
        )

    def fix_all_users(self):
        """Assign default groups to users without any groups"""
        self.stdout.write('🔧 FIXING USERS WITHOUT GROUPS...')
        self.stdout.write('=' * 40)
        
        users_without_groups = []
        for user in User.objects.all():
            if not user.groups.exists() and not user.is_superuser:
                users_without_groups.append(user)

        if not users_without_groups:
            self.stdout.write(self.style.SUCCESS('✅ All users already have groups assigned!'))
            return

        self.stdout.write(f'Found {len(users_without_groups)} users without groups:')
        
        # Get default group (Commerciaux)
        try:
            default_group = Group.objects.get(name='Commerciaux')
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Default group "Commerciaux" not found'))
            self.stdout.write('Please run "python manage.py setup_groups" first')
            return

        for user in users_without_groups:
            user.groups.add(default_group)
            self.stdout.write(f'   ✅ Assigned {user.username} to {default_group.name}')

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Successfully assigned {len(users_without_groups)} users to default group!')
        )
