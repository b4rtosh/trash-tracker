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

    # Local apps
    'apps.routes'
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
STATIC_URL = '/web/'
STATICFILES_DIRS = [
    BASE_DIR / 'web/static',
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
