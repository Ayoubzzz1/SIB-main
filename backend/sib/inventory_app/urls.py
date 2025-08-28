from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MatierePremiereViewSet, ProduitSemiFiniViewSet, ProduitFiniViewSet, 
    StockViewSet, MouvementStockViewSet
)

router = DefaultRouter()
router.register(r'matieres-premieres', MatierePremiereViewSet)
router.register(r'produits-semi-finis', ProduitSemiFiniViewSet)
router.register(r'produits-finis', ProduitFiniViewSet)
router.register(r'stock', StockViewSet)
router.register(r'mouvements-stock', MouvementStockViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
