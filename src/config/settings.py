import os
import sys
from pathlib import Path
import environ


BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
# Modify INSTALLED_APPS to use apps in the apps directory
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    # Local apps
    'apps.routes',
    'apps.accounts',
]

# Add middleware configuration - this was missing
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.accounts.middleware.LoginRequiredMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Add ROOT_URLCONF setting
ROOT_URLCONF = 'config.urls'

STATIC_URL = '/static/'

# Add this to tell Django where to look for static files
STATICFILES_DIRS = [
    BASE_DIR / "web/staticapp",  # Adjust the path based on your directory structure
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'web/templates'
        ],
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

DATABASES = {
    "default": {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'trash_tracker',
            'USER': 'admin',
            'PASSWORD': 'adminpass',
            'HOST': 'localhost',
            'PORT': '3306',
        },
}

# Update the base directory for Python to find apps
sys.path.insert(0, str(BASE_DIR / 'apps'))
DJANGO_TEMPLATE_DEBUG = True
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = "/routes/"
LOGOUT_REDIRECT_URL = '/accounts/login/'

SESSION_COOKIE_AGE = 60
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@example.com'