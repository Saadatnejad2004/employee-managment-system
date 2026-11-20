from django import forms
from .models import Employee, Department

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'phone', 'job_title', 
                  'salary_cents', 'date_hired', 'status', 'department']
        widgets = {
            'date_hired': forms.DateInput(attrs={'type': 'date'}),
            'salary_cents': forms.NumberInput(attrs={'placeholder': 'e.g., 5000000 for $50,000'}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'budget_cents']
