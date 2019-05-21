import os

from decouple import config
from dj_database_url import parse as db_url


SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.dirname(SETTINGS_DIR)
PROJECT_DIR = os.path.dirname(CONFIG_DIR)
BASE_DIR = os.path.dirname(PROJECT_DIR)

DEBUG = config('DEBUG', default=False, cast=bool)

#
#  Django-specific settings
#

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'core.RadioUser'

DATABASES = {
    'default': config(
        'DATABASE_URL',
        default='sqlite:///' + os.path.join(PROJECT_DIR, 'spradio.sqlite3'),
        cast=db_url
    )
}

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'authtools',
    'rest_framework',
    'rest_framework.authtoken',

    'core.apps.CoreConfig',
    'radio.apps.RadioConfig',
    'profiles.apps.ProfilesConfig',
    'api.apps.ApiConfig',
]

LANGUAGE_CODE = 'en-us'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

ROOT_URLCONF = 'savepointradio.urls'

SECRET_KEY = config('SECRET_KEY')

SITE_ID = 1

STATIC_URL = '/static/'

STATIC_ROOT = config('STATIC_ROOT',
                     default=os.path.join(PROJECT_DIR, 'static/'))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

TIME_ZONE = config('TIME_ZONE', default='America/New_York')

USE_I18N = True

USE_L10N = True

USE_TZ = True

WSGI_APPLICATION = 'savepointradio.wsgi.application'

#
#  Django Rest Framework settings
#

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.TotalPagesPagination',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'PAGE_SIZE': 100,
}

#
#  Radio-specific settings
#

RADIO_DJ_EMAIL = config('RADIO_DJ_EMAIL', default='dj@radiostation.net')

RADIO_DJ_NAME = config('RADIO_DJ_NAME', default='DJ Reinhardt')
