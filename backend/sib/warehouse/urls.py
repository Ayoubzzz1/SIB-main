from rest_framework.routers import DefaultRouter
from .views import EntrepotViewSet

router = DefaultRouter()
router.register(r'entrepots', EntrepotViewSet)
 
urlpatterns = router.urls 