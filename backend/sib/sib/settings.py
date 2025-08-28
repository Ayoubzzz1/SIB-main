from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-0=61gv5x=!d6dh)(y=m@nx-*_g4(6hku#^m-ha_d5aw8q^k8z'

DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

# Allow localhost and internal network during development
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

INSTALLED_APPS = [
    'jazzmin',  # Must be FIRST - replaces admin_interface

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',

    # Django REST Framework
    'rest_framework',
    'rest_framework.authtoken',

    # CORS headers
    'corsheaders',

    # Custom apps
    'users_app',
    'inventory_app',
    'sales_app',
    'production_app',
    'communication_app',
    'logs_app',
    'warehouse',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be first
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'sib.middleware.AllowAllUsersAdminMiddleware',  # Allow any user to access admin
    'users_app.middleware.WarehouseAccessMiddleware',  # Add warehouse access info to requests
    'users_app.middleware.WarehouseFilterMiddleware',  # Filter data by warehouse access
]

ROOT_URLCONF = 'sib.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sib.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files configuration
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization', 'content-type',
    'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with',
]

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# Jazzmin Configuration with Red Theme and Logo
JAZZMIN_SETTINGS = {
    # Main Settings with Logo
    "site_title": "SIB Admin",
    "site_header": "Administration SIB",
    "site_brand": "SIB",
    "site_logo": "images/logo.png",  # Logo in sidebar
    "login_logo": "images/logo.png",  # Logo on login page
    "login_logo_dark": "images/logo.png",  # Logo for dark mode login
    "site_logo_classes": "",  # Square logo (remove img-circle for square)
    "site_icon": "images/logo.png",  # Favicon (browser tab icon)
    "welcome_sign": "Bienvenue dans l'administration SIB",
    "copyright": "SIB Company © 2025",
    "search_model": ["auth.User", "inventory_app.MatierePremiere", "sales_app.Client"],
    "user_avatar": None,
    "show_recent_actions": False,

    # Top Menu Links
   

    # User Menu on the right
    "usermenu_links": [
        {"name": "Mon Profil", "url": "admin:auth_user_change", "icon": "fas fa-user"},
        {"name": "Support", "url": "mailto:support@sib.com", "new_window": True},
        {"model": "auth.user"}
    ],

    # Side Menu Settings
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],

    # Order of apps in sidebar
    "order_with_respect_to": [
        "auth",
        "users_app", 
        "inventory_app", 
        "sales_app",
        "production_app", 
        "communication_app", 
        "logs_app", 
        "warehouse"
    ],

    # Custom icons for apps and models - Red theme compatible
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "users_app": "fas fa-user-friends",
        "users_app.Utilisateur": "fas fa-user",
        "users_app.UtilisateurEntrepot": "fas fa-user-tie",
        "inventory_app": "fas fa-boxes",
        "inventory_app.MatierePremiere": "fas fa-cubes",
        "inventory_app.ProduitSemiFini": "fas fa-cogs",
        "inventory_app.ProduitFini": "fas fa-box",
        "inventory_app.Stock": "fas fa-warehouse",
        "inventory_app.MouvementStock": "fas fa-exchange-alt",
        "sales_app": "fas fa-shopping-cart",
        "sales_app.Client": "fas fa-user-tag",
        "sales_app.Fournisseur": "fas fa-truck",
        "sales_app.Commande": "fas fa-file-invoice",
        "sales_app.ArticleCommande": "fas fa-list",
        "production_app": "fas fa-industry",
        "production_app.Production": "fas fa-cogs",
        "production_app.NomenclatureProduits": "fas fa-clipboard-list",
        "communication_app": "fas fa-comments",
        "communication_app.Message": "fas fa-envelope",
        "logs_app": "fas fa-clipboard-list",
        "logs_app.Log": "fas fa-file-alt",
        "warehouse": "fas fa-building",
        "warehouse.Entrepot": "fas fa-warehouse",
    },

    # Custom Links in specific apps
    "custom_links": {
        "inventory_app": [
            {
                "name": "Rapport de Stock", 
                "url": "admin:inventory_app_stock_changelist", 
                "icon": "fas fa-chart-bar",
                "permissions": ["inventory_app.view_stock"]
            }
        ],
        "sales_app": [
            {
                "name": "Nouveau Client", 
                "url": "admin:sales_app_client_add", 
                "icon": "fas fa-user-plus",
                "permissions": ["sales_app.add_client"]
            }
        ]
    },

    # Related Modal
    "related_modal_active": False,

    # UI Customization
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,

    # Change form layout
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible", 
        "auth.group": "vertical_tabs",
        "inventory_app.matierepremiere": "horizontal_tabs",
    },

    # Language chooser - disabled to avoid i18n URL issues
    "language_chooser": False,
}

# Jazzmin UI Tweaks - Custom Color Scheme
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-light",  # White navbar brand
    "accent": "accent-danger",  # Red accent color for links
    "navbar": "navbar-light bg-white",  # White navbar with black text
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-danger",  # Red sidebar with white text
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",  # Base theme
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-danger",  # Red primary buttons
        "secondary": "btn-outline-secondary", 
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-danger",  # Red danger buttons
        "success": "btn-outline-success"
    },
    "actions_sticky_top": False,
}