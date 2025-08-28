from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users_app.models import Utilisateur

class Command(BaseCommand):
    help = 'Create Utilisateur profiles for existing users that don\'t have them'

    def handle(self, *args, **options):
        users_without_profiles = []
        
        for user in User.objects.all():
            try:
                user.utilisateur
            except Utilisateur.DoesNotExist:
                users_without_profiles.append(user)
        
        if not users_without_profiles:
            self.stdout.write(
                self.style.SUCCESS('All users already have Utilisateur profiles!')
            )
            return
        
        self.stdout.write(f'Found {len(users_without_profiles)} users without profiles...')
        
        for user in users_without_profiles:
            # Determine role based on user permissions
            if user.is_superuser:
                role = 'admin'
            elif user.is_staff:
                role = 'admin'
            else:
                role = 'commercial'
            
            # Create the profile
            Utilisateur.objects.create(
                user=user,
                nom=user.username,
                role=role
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created profile for {user.username} with role: {role}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(users_without_profiles)} user profiles!')
        ) 