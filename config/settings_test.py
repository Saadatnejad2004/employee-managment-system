"""Settings used by the test suite: identical to production, but faster."""

from .settings import *  # noqa: F403

# PBKDF2 is deliberately slow; tests create many users, so use a fast hasher.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# The manifest storage needs `collectstatic` to have run; tests don't need that.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# No `collectstatic` in tests, so WhiteNoise would only warn about a missing directory.
MIDDLEWARE = [m for m in MIDDLEWARE if "whitenoise" not in m]  # noqa: F405
