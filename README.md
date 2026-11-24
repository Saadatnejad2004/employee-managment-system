# Employee Management System (Django)

A server-side rendered application built with Python and Django to manage employee records, departments, and generate organizational reports.

## Tech Stack
- Python 3.12+
- Django 6.1 (MVT Architecture)
- PostgreSQL (Docker / production) with trigram search indexes; SQLite for quick local development
- Gunicorn + WhiteNoise, Docker Compose
- Django ORM (Object-Relational Mapper)
- HTML/CSS (Custom UI)

## Key Features
- **Employee Records:** Full CRUD with ModelForms and unique email validation.
- **Department Management:** Relational database design (1-to-Many). Cannot delete a department if employees are assigned.
- **Search & Pagination:** Server-side search (`icontains`) and pagination (10 per page) to handle large datasets efficiently.
- **Reports Dashboard:** ORM Aggregations (`Sum`, `Count`, `Avg`) to calculate total payroll and department breakdowns.
- **Performance Optimization:** Demonstrated mitigation of the N+1 Query Problem using `select_related` and `annotate`.
- **Authentication & Role-Based Access:** Login-required by default (`LoginRequiredMiddleware`), three roles with row-level scoping and field-level salary visibility.

## Roles

| Role | Employees | Salary | Departments | Dashboard |
|---|---|---|---|---|
| **HR Admin** | All; create / edit / delete | Everyone's | View / add | Yes |
| **Manager** | Own department, read-only | Own only | No | No |
| **Employee** | Own profile, read-only | Own only | No | No |

Roles are Django groups defined in `employees/roles.py` and created by `python manage.py setup_roles`.
A login account is linked to an employee record via the `user` field (set in the Django admin);
that link is how the system knows a manager's department.

## Getting Started

### Option A: Docker (production-like: PostgreSQL + Gunicorn)
```bash
cp .env.example .env            # then edit .env: set DJANGO_SECRET_KEY (and an admin login, see below)
docker compose up --build
```
Open http://localhost:8000. Migrations and `setup_roles` run automatically on start.
To get a first admin account, set `DJANGO_SUPERUSER_USERNAME` and `DJANGO_SUPERUSER_PASSWORD`
in `.env` before the first start, or run `docker compose exec web python manage.py createsuperuser`.
Health check: `/healthz/`. Data lives in the `pgdata` volume (`docker compose down -v` wipes it).

### Option B: Local Python (SQLite)
1. `python -m venv venv` and activate it (`source venv/bin/activate`, or `venv\Scripts\activate` on Windows)
2. `pip install -r requirements-dev.txt`
3. `cp .env.example .env` (it already contains `DJANGO_DEBUG=1`)
4. `python manage.py migrate && python manage.py setup_roles && python manage.py createsuperuser`
5. `python manage.py runserver`, then visit http://127.0.0.1:8000/

### Configuration
Everything is an environment variable (or a line in `.env`); see `.env.example`.
`DATABASE_URL` selects the database (`sqlite:///...` or `postgres://user:pass@host:5432/db`).
With `DJANGO_DEBUG` off, `DJANGO_SECRET_KEY` is required and HTTPS settings turn on
(redirect, secure cookies, HSTS); set `DJANGO_HTTPS=0` to try that mode over plain http,
and `DJANGO_BEHIND_PROXY=1` when a TLS-terminating proxy sits in front.

### Creating users
In `/admin/`: create a **User**, add it to a group (HR Admin / Manager / Employee), then open the
matching **Employee** record and pick that user in the `user` field. Terminating an employee
automatically deactivates their login.

## Development

```bash
pip install -r requirements-dev.txt
pre-commit install        # runs ruff (lint + format) on every commit
pytest                    # ~80 tests, a few seconds, coverage must stay >= 90%
ruff check . && ruff format --check .
```

Tests use `pytest-django` with `factory_boy` factories (`employees/tests/factories.py`);
`config/settings_test.py` swaps in a fast password hasher. CI (`.github/workflows/ci.yml`)
runs lint, format check, `manage.py check`, a missing-migrations check and the test suite
(against PostgreSQL), then builds the Docker image and boots the stack, on every push and pull request.
The PostgreSQL-only trigram index tests are skipped on SQLite and run in CI.
