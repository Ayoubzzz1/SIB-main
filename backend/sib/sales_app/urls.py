from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, CommandeViewSet, ArticleCommandeViewSet, FournisseurViewSet

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'fournisseurs', FournisseurViewSet)
router.register(r'commandes', CommandeViewSet)
router.register(r'articles-commande', ArticleCommandeViewSet)

urlpatterns = router.urls
