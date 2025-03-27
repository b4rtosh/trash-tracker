import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Modify INSTALLED_APPS to use apps in the apps directory
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local apps
    'apps.core',
    'apps.items',
    'apps.frontend',

    # Third-party apps
    'rest_framework',
]

# Add middleware configuration - this was missing
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Add ROOT_URLCONF setting
ROOT_URLCONF = 'config.urls'

# Update static and template directories
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'frontend/static',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'apps/frontend/templates'],
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

# Add SECRET_KEY - this is required for Django to run
SECRET_KEY = 'django-insecure-temporary-key-for-development-only'

# Update the base directory for Python to find apps
sys.path.insert(0, str(BASE_DIR / 'apps'))
DEBUG = True
DJANGO_TEMPLATE_DEBUG = True
