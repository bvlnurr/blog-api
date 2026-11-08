from settings.base import *

from decouple import config


DEBUG = False

ALLOWED_HOSTS = config(
    "BLOG_ALLOWED_HOSTS",
    default="",
    cast=lambda value: [
        host.strip()
        for host in value.split(",")
        if host.strip()
    ],
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("BLOG_DB_NAME"),
        "USER": config("BLOG_DB_USER"),
        "PASSWORD": config("BLOG_DB_PASSWORD"),
        "HOST": config("BLOG_DB_HOST"),
        "PORT": config("BLOG_DB_PORT", default="5432"),
    }
}