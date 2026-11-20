from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Count, Avg
from .models import Employee, Department
from .forms import EmployeeForm, DepartmentForm

# ============ EMPLOYEE VIEWS ============

class EmployeeListView(ListView):
    model = Employee
    template_name = "employees/employee_list.html"
    context_object_name = "employees"
    paginate_by = 10  # Built-in pagination (10 per page)

    def get_queryset(self):
        # Start with all employees, optimize the query using select_related
        queryset = super().get_queryset().select_related('department').order_by('-date_hired', 'last_name')
        
        # Handle search
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query) |
                Q(job_title__icontains=query)
            )
        return queryset

class EmployeeCreateView(CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/employee_form.html"
    success_url = reverse_lazy("employee_list")

class EmployeeUpdateView(UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/employee_form.html"
    success_url = reverse_lazy("employee_list")

class EmployeeDeleteView(DeleteView):
    model = Employee
    template_name = "employees/employee_confirm_delete.html"
    success_url = reverse_lazy("employee_list")


# ============ DEPARTMENT VIEWS ============

class DepartmentListView(ListView):
    model = Department
    template_name = "employees/department_list.html"
    context_object_name = "departments"

    # Annotate the queryset with the employee count
    def get_queryset(self):
        return Department.objects.annotate(emp_count=Count('employees'))

class DepartmentCreateView(CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = "employees/department_form.html"
    success_url = reverse_lazy("department_list")


# ============ DASHBOARD REPORT ============

class DashboardView(TemplateView):
    template_name = "employees/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Headcounts
        context['total_employees'] = Employee.objects.count()
        context['active_employees'] = Employee.objects.filter(status='active').count()
        
        # 2. Financials (Aggregation)
        # This executes a single SQL query: SELECT SUM(salary_cents) FROM employee...
        payroll = Employee.objects.aggregate(total=Sum('salary_cents'))
        context['total_payroll_dollars'] = (payroll['total'] or 0) / 100
        
        avg_salary = Employee.objects.aggregate(avg=Avg('salary_cents'))
        context['avg_salary_dollars'] = (avg_salary['avg'] or 0) / 100

        # 3. Department Breakdown (GROUP BY)
        # This joins departments and employees, groups by department, and counts/sums.
        context['departments'] = Department.objects.annotate(
            emp_count=Count('employees'),
            dept_payroll=Sum('employees__salary_cents')
        ).order_by('-emp_count')
        
        return context
