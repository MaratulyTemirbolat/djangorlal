# Project modules
from decouple import config

# ----------------------------------------------
# Env id
#
ENV_POSSIBLE_OPTIONS = (
    "local",
    "prod",
)
ENV_ID = config("DJANGORLAR_ENV_ID", cast=str)
SECRET_KEY = 'django-insecure-tqxyifr^9iaznii9*b4xpdmi08h*19p-eh0g%gx4n=%9nu2!d2'
