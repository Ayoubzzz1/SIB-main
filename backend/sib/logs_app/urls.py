from rest_framework.routers import DefaultRouter
from .views import HistoriqueActiviteViewSet

router = DefaultRouter()
router.register(r'historique-activites', HistoriqueActiviteViewSet)

urlpatterns = router.urls
