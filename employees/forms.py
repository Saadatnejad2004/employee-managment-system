from decimal import Decimal

from django import forms

from .models import Department, Employee
from .money import MAX_CENTS, cents_to_dollars, dollars_to_cents


def dollars_field(label, help_text=""):
    """A form field that takes dollars (e.g. 50000.00); the model stores cents."""
    return forms.DecimalField(
        label=label,
        help_text=help_text,
        min_value=Decimal("0"),
        max_value=cents_to_dollars(MAX_CENTS),
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"step": "0.01", "placeholder": "e.g. 50000.00"}),
    )


class EmployeeForm(forms.ModelForm):
    salary = dollars_field("Salary (USD per year)")

    field_order = [
        "first_name",
        "last_name",
        "email",
        "phone",
        "job_title",
        "salary",
        "date_hired",
        "status",
        "department",
    ]

    class Meta:
        model = Employee
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "job_title",
            "date_hired",
            "status",
            "department",
        ]
        widgets = {
            "date_hired": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial["salary"] = cents_to_dollars(self.instance.salary_cents)

    def clean_email(self):
        # Emails are case-insensitive in practice: store lowercase and make
        # uniqueness case-insensitive too.
        email = self.cleaned_data["email"].strip().lower()
        clash = Employee.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if clash.exists():
            raise forms.ValidationError("An employee with this email already exists.")
        return email

    def save(self, commit=True):
        self.instance.salary_cents = dollars_to_cents(self.cleaned_data["salary"])
        return super().save(commit=commit)


class DepartmentForm(forms.ModelForm):
    budget = dollars_field("Budget (USD)")

    field_order = ["name", "description", "budget"]

    class Meta:
        model = Department
        fields = ["name", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial["budget"] = cents_to_dollars(self.instance.budget_cents)

    def save(self, commit=True):
        self.instance.budget_cents = dollars_to_cents(self.cleaned_data["budget"])
        return super().save(commit=commit)
