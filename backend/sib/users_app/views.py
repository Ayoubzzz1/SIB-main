from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Utilisateur
from .serializers import UtilisateurSerializer, UserSerializer # Import UserSerializer
from .permissions import IsAdmin, IsAdminOrReadOnly, CanManageUsers
from logs_app.mixins import LoggingMixin
from django.core.exceptions import ObjectDoesNotExist

class UtilisateurViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all().select_related('user')
    serializer_class = UtilisateurSerializer
    permission_classes = [CanManageUsers]  # Only admins can manage users

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Utilisateur.objects.none()

        # Check if user is superuser or staff
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Utilisateur.objects.all().select_related('user')

        # Check if user belongs to Administrateurs group
        if self.request.user.groups.filter(name='Administrateurs').exists():
            return Utilisateur.objects.all().select_related('user')
        
        # Regular users can only see their own profile
        return Utilisateur.objects.filter(user=self.request.user).select_related('user')

    def destroy(self, request, *args, **kwargs):
        """Override destroy method to handle cascade deletion properly"""
        try:
            instance = self.get_object()
            # Delete the Django User first, which will cascade to Utilisateur
            if instance.user:
                instance.user.delete()
            else:
                instance.delete()
            return Response(status=204)
        except Exception as e:
            return Response(
                {"detail": f"Failed to delete user: {str(e)}"}, 
                status=400
            )

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_profile = request.user.utilisateur
            serializer = UtilisateurSerializer(user_profile)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response(
                {"detail": "User profile not found"}, 
                status=404
            )
