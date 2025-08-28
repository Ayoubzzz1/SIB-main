from django.apps import AppConfig


class InventoryAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory_app'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            import inventory_app.signals
        except ImportError:
            pass
