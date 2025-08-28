"""
URL configuration for sib project with Unfold UI.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

# Import routers from each application
from users_app.urls import router as users_router
from inventory_app.urls import router as inventory_router
from sales_app.urls import router as sales_router
from production_app.urls import router as production_router
from communication_app.urls import router as communication_router
from logs_app.urls import router as logs_router
from warehouse.urls import router as warehouse_router

# Create a main router for all APIs
router = DefaultRouter()
# If you need to enable users API in the main router, uncomment the next line
# router.registry.extend(users_router.registry)
router.registry.extend(inventory_router.registry)
router.registry.extend(sales_router.registry)
router.registry.extend(production_router.registry)
router.registry.extend(communication_router.registry)
router.registry.extend(logs_router.registry)
router.registry.extend(warehouse_router.registry)

urlpatterns = [
    # Redirect root to admin for better UX
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    
    # Add i18n support for language switching (Unfold supports this)
    path('i18n/', include('django.conf.urls.i18n')),
    
    # Django admin with Unfold UI
    path('admin/', admin.site.urls),
    
    # Password reset URLs for Unfold
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # API endpoints with better organization
    path('api/v1/', include([
        # Main API router
        path('', include(router.urls)),
        # Specific app endpoints
        path('users/', include('users_app.urls')),
        path('inventory/', include('inventory_app.urls')), 
        path('sales/', include('sales_app.urls')),
        path('production/', include('production_app.urls')),
        path('communication/', include('communication_app.urls')),
        path('logs/', include('logs_app.urls')),
        path('warehouse/', include('warehouse.urls')),
    ])),
    
    # Legacy API endpoint for backward compatibility
    path('api/', include(router.urls)),
    path('api/users/', include('users_app.urls')),
    
    # Authentication endpoints
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    path('token/', obtain_auth_token, name='api_token_auth_legacy'),  # Legacy support
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site headers and titles for Unfold
admin.site.site_header = 'Administration SIB'
admin.site.site_title = 'SIB Admin'
admin.site.index_title = 'Bienvenue dans l\'administration SIB'
admin.site.site_url = '/'  # Link back to main site
# admin.site.enable_nav_sidebar = False  # Let Unfold handle sidebar - REMOVED this line!