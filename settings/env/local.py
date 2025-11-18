# Project modules
from settings.base import *


DEBUG = True
ALLOWED_HOSTS = []
INTERNAL_IPS = [
    "127.0.0.1",
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    },
}