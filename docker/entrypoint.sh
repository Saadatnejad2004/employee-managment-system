#!/bin/sh
# Runs before the web server starts. Everything here is safe to repeat.
set -e

if [ "${DJANGO_MIGRATE:-1}" = "1" ]; then
    python manage.py migrate --noinput
    python manage.py setup_roles
fi

# Optional first-run admin: set DJANGO_SUPERUSER_USERNAME and
# DJANGO_SUPERUSER_PASSWORD (and optionally DJANGO_SUPERUSER_EMAIL).
# Skipped silently if that user already exists.
if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    python manage.py createsuperuser --noinput \
        --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" 2>/dev/null \
        && echo "Created superuser ${DJANGO_SUPERUSER_USERNAME}" \
        || echo "Superuser ${DJANGO_SUPERUSER_USERNAME} already exists (or could not be created)"
fi

exec "$@"
