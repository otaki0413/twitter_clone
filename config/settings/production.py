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

# --------------------
# Email settings
# --------------------
FROM_EMAIL = env("FROM_EMAIL")
EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
ANYMAIL = {"SENDGRID_API_KEY": env("SENDGRID_API_KEY")}
