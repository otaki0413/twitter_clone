import environ
import dj_database_url

from .base import *


env = environ.Env()

# --------------------
# Security settings
# --------------------
DEBUG = False

SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = [".herokuapp.com"]


# --------------------
# Database
# --------------------
DATABASES = {
    "default": dj_database_url.config(
        env="DATABASE_URL",
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    )
}
