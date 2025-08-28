from django.contrib.auth.models import User
from django.contrib.auth import get_user

class AllowAllUsersAdminMiddleware:
    """
    Middleware that allows any authenticated user to access the Django admin.
    This bypasses the default staff requirement.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if this is an admin request
        if request.path.startswith('/admin/'):
            # If user is authenticated, make them staff temporarily
            if request.user.is_authenticated:
                # Temporarily set is_staff to True for admin access
                if not request.user.is_staff:
                    request.user.is_staff = True
                    request.user.is_superuser = True
        
        response = self.get_response(request)
        return response

