from django.apps import AppConfig


class WarehouseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'warehouse'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            import warehouse.signals
        except ImportError:
            pass
