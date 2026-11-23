# Employee Management System (Django)

A server-side rendered application built with Python and Django to manage employee records, departments, and generate organizational reports.

## Tech Stack
- Python 3.12+
- Django 6.1 (MVT Architecture)
- SQLite (Development Database)
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
1. `python -m venv venv`
2. `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
3. `pip install -r requirements.txt`
4. Set `DJANGO_DEBUG=1` for local development (see `.env.example`). Outside debug mode `DJANGO_SECRET_KEY` is required.
5. `python manage.py migrate`
6. `python manage.py setup_roles`
7. `python manage.py createsuperuser`
8. `python manage.py runserver`
9. Visit `http://127.0.0.1:8000/` and sign in.

### Creating users
In `/admin/`: create a **User**, add it to a group (HR Admin / Manager / Employee), then open the
matching **Employee** record and pick that user in the `user` field. Terminating an employee
automatically deactivates their login.

## Tests
`DJANGO_DEBUG=1 python manage.py test`
