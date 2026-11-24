from django.contrib.auth.decorators import login_not_required
from django.db import OperationalError, connection
from django.db.models import Avg, Count, Q, Sum
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import DepartmentForm, EmployeeForm
from .models import Department, Employee

# Authentication is enforced globally by LoginRequiredMiddleware.
# We only handle view logic here.

# ============ EMPLOYEE VIEWS ============


class EmployeeListView(ListView):
    model = Employee
    template_name = "employees/employee_list.html"
    context_object_name = "employees"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            super().get_queryset().select_related("department").order_by("-date_hired", "last_name")
        )
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query)
                | Q(job_title__icontains=query)
            )
        return queryset


class EmployeeDetailView(DetailView):
    model = Employee
    template_name = "employees/employee_detail.html"
    context_object_name = "employee"


class MyProfileView(DetailView):
    model = Employee
    template_name = "employees/my_profile.html"
    context_object_name = "employee"

    def get_object(self, queryset=None):
        # Assuming you link the User to the Employee via email (or a user field)
        # If you added a `user = models.OneToOneField(User)` to your Employee model,
        # change this to `return self.request.user.employee`
        employee = Employee.objects.filter(email=self.request.user.email).first()
        if not employee:
            # Fallback if no employee record exists for this user
            from django.http import Http404

            raise Http404("No Employee profile found for this user.")
        return employee


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

    def get_queryset(self):
        return Department.objects.annotate(emp_count=Count("employees"))


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
        context["total_employees"] = Employee.objects.count()
        context["active_employees"] = Employee.objects.filter(status="active").count()

        payroll = Employee.objects.aggregate(total=Sum("salary_cents"))
        context["total_payroll_dollars"] = (payroll["total"] or 0) / 100

        avg_salary = Employee.objects.aggregate(avg=Avg("salary_cents"))
        context["avg_salary_dollars"] = (avg_salary["avg"] or 0) / 100

        context["departments"] = Department.objects.annotate(
            emp_count=Count("employees"), dept_payroll=Sum("employees__salary_cents")
        ).order_by("-emp_count")

        return context


# ============ OPERATIONS ============


@login_not_required
def healthz(request):
    """Liveness + database check for Docker / load balancers."""
    try:
        connection.ensure_connection()
    except OperationalError:
        return JsonResponse({"status": "database unavailable"}, status=503)
    return JsonResponse({"status": "ok"})
