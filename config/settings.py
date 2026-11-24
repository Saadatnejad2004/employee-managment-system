"""
Django settings for config project.

All configuration comes from environment variables. For local development put
them in a `.env` file next to manage.py (see .env.example); in Docker/production
set real environment variables. No secret is ever committed to the repository.
"""

from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
if (BASE_DIR / ".env").exists():  # real environment variables always win over .env
    environ.Env.read_env(BASE_DIR / ".env")


# --------------------------------------------------------------------------
# Core / secrets
# --------------------------------------------------------------------------

# Secure by default: DEBUG is OFF unless you explicitly set DJANGO_DEBUG=1.
DEBUG = env.bool("DJANGO_DEBUG", default=False)

SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="")
if not SECRET_KEY:
    if DEBUG:
        # Throw-away key for local development only.
        SECRET_KEY = "django-insecure-dev-only-key-do-not-use-in-production"
    else:
        raise ImproperlyConfigured(
            "The DJANGO_SECRET_KEY environment variable is required when DEBUG is off."
        )

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])


# --------------------------------------------------------------------------
# Applications
# --------------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "employees",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Every view requires a logged-in user unless it is explicitly decorated
    # with @login_not_required. Must come AFTER AuthenticationMiddleware.
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if not DEBUG:
    # Serves the collected static files straight from Gunicorn (no nginx needed).
    # In development `runserver` serves static files itself.
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# --------------------------------------------------------------------------
# Database
# --------------------------------------------------------------------------
# DATABASE_URL examples:
#   sqlite:///path/to/db.sqlite3                     (default for local dev)
#   postgres://user:password@host:5432/dbname        (Docker / production)
# Special characters in the password must be URL-encoded.

DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
}
DATABASES["default"]["CONN_MAX_AGE"] = 60  # reuse connections between requests
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True  # ...but drop dead ones


# --------------------------------------------------------------------------
# Authentication & sessions
# --------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "employee_list"
LOGOUT_REDIRECT_URL = "login"

SESSION_COOKIE_AGE = 60 * 60 * 8  # 8-hour working-day sessions


# --------------------------------------------------------------------------
# HTTPS
# --------------------------------------------------------------------------
# On by default whenever DEBUG is off. To try a production-like container over
# plain http://localhost, set DJANGO_HTTPS=0 (docker compose does this for you).

HTTPS = env.bool("DJANGO_HTTPS", default=not DEBUG)

SESSION_COOKIE_SECURE = HTTPS
CSRF_COOKIE_SECURE = HTTPS
SECURE_SSL_REDIRECT = HTTPS
SECURE_REDIRECT_EXEMPT = [r"^healthz/$"]  # container health checks speak plain http
SECURE_HSTS_SECONDS = env.int("DJANGO_HSTS_SECONDS", default=3600 if HTTPS else 0)

# Set when running behind a TLS-terminating reverse proxy (nginx, Caddy, a cloud
# load balancer) that sends X-Forwarded-Proto. Only enable if the proxy strips
# that header from client requests, otherwise it can be spoofed.
if env.bool("DJANGO_BEHIND_PROXY", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# --------------------------------------------------------------------------
# Internationalization
# --------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# --------------------------------------------------------------------------
# Static files
# --------------------------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # target of `collectstatic`
STATICFILES_DIRS = [BASE_DIR / "static"]

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        # Hashed, compressed, long-cache filenames in production (needs collectstatic).
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}


# --------------------------------------------------------------------------
# Logging (to stdout, which is where Docker and most hosts collect logs)
# --------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"plain": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "plain"}},
    "root": {"handlers": ["console"], "level": env.str("DJANGO_LOG_LEVEL", default="INFO")},
}

# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}
