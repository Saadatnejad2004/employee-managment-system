# Employee Management System (Django)

A server-side rendered application built with Python and Django to manage employee records, departments, and generate organizational reports.

## Tech Stack
- Python 3.12+
- Django 5.x (MVT Architecture)
- SQLite (Development Database)
- Django ORM (Object-Relational Mapper)
- HTML/CSS (Custom UI)

## Key Features
- **Employee Records:** Full CRUD with ModelForms and unique email validation.
- **Department Management:** Relational database design (1-to-Many). Cannot delete a department if employees are assigned.
- **Search & Pagination:** Server-side search (`icontains`) and pagination (10 per page) to handle large datasets efficiently.
- **Reports Dashboard:** ORM Aggregations (`Sum`, `Count`, `Avg`) to calculate total payroll and department breakdowns.
- **Performance Optimization:** Demonstrated mitigation of the N+1 Query Problem using `select_related` and `annotate`.

## Getting Started
1. `python -m venv venv`
2. `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
3. `pip install django`
4. `python manage.py migrate`
5. `python manage.py runserver`
6. Visit `http://127.0.0.1:8000/`
