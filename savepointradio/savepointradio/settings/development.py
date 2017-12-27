from decouple import config
from dj_database_url import parse as db_url

from .base import *


ALLOWED_HOSTS = []

DATABASES = {
    'default': config(
        'DATABASE_URL',
        default='sqlite:///' + os.path.join(PROJECT_DIR, 'testdb.sqlite3'),
        cast=db_url
    )
}

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'