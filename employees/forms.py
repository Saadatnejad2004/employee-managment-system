from django import forms

from .models import Department, Employee

INPUT_CLASSES = (
    "w-full px-4 py-2.5 rounded-lg border border-gray-300 "
    "focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 "
    "outline-none transition"
)


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "job_title",
            "salary_cents",
            "date_hired",
            "status",
            "department",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "Jane"}),
            "last_name": forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "Doe"}),
            "email": forms.EmailInput(
                attrs={"class": INPUT_CLASSES, "placeholder": "jane@example.com"}
            ),
            "phone": forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "+1 555-0199"}),
            "job_title": forms.TextInput(
                attrs={"class": INPUT_CLASSES, "placeholder": "Software Engineer"}
            ),
            "salary_cents": forms.NumberInput(
                attrs={"class": INPUT_CLASSES, "placeholder": "e.g., 8500000"}
            ),
            "date_hired": forms.DateInput(attrs={"class": INPUT_CLASSES, "type": "date"}),
            "status": forms.Select(attrs={"class": INPUT_CLASSES}),
            "department": forms.Select(attrs={"class": INPUT_CLASSES}),
        }


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "description", "budget_cents"]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "Engineering"}),
            "description": forms.Textarea(attrs={"class": INPUT_CLASSES, "rows": 3}),
            "budget_cents": forms.NumberInput(
                attrs={"class": INPUT_CLASSES, "placeholder": "e.g., 50000000"}
            ),
        }
