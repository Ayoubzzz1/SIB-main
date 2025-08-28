from rest_framework.routers import DefaultRouter
# from django.urls import path # path n'est plus nécessaire si get_related_objects_json est supprimé
from .views import ProductionViewSet, MatiereProductionViewSet, NomenclatureProduitsViewSet # , get_related_objects_json

router = DefaultRouter()
router.register(r'production', ProductionViewSet)
router.register(r'matieres-production', MatiereProductionViewSet)
router.register(r'nomenclature-produits', NomenclatureProduitsViewSet)

# Supprimez la ligne suivante
# urlpatterns = router.urls + [
#     path('get-related-objects/', get_related_objects_json, name='get_related_objects_json'),
# ]

# La liste d'URL redevient simplement le routeur
urlpatterns = router.urls
