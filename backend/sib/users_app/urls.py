from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import UtilisateurViewSet, CurrentUserView

router = DefaultRouter()
router.register(r'utilisateurs', UtilisateurViewSet)

urlpatterns = router.urls + [
    path('me/', CurrentUserView.as_view(), name='current_user_profile'),
]
