from django.core.management.base import BaseCommand
from logs_app.models import HistoriqueActivite
from users_app.models import Utilisateur

class Command(BaseCommand):
    help = 'Check activity logs in the database'

    def handle(self, *args, **options):
        total_logs = HistoriqueActivite.objects.count()
        self.stdout.write(f"Total activity logs: {total_logs}")
        
        if total_logs > 0:
            self.stdout.write("Recent logs:")
            for log in HistoriqueActivite.objects.all()[:5]:
                self.stdout.write(f"  - {log}")
        else:
            self.stdout.write("No activity logs found in database")
            
        # Check if there are any users with admin role
        admin_users = Utilisateur.objects.filter(role='admin')
        self.stdout.write(f"Admin users: {admin_users.count()}")
        for user in admin_users:
            self.stdout.write(f"  - {user.nom} ({user.user.username})") 