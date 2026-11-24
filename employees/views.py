from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import OperationalError, connection
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
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
from .permissions import EmployeeScopeMixin, can_view_salary
from .reports import PAYABLE_STATUSES, company_summary, department_breakdown

# Authentication ("are you logged in?") is enforced globally by
# LoginRequiredMiddleware. Everything below is AUTHORIZATION:
#   PermissionRequiredMixin -> may this user use this screen at all? (403)
#   EmployeeScopeMixin      -> which employee rows may they touch?   (404)

# ============ EMPLOYEE VIEWS ============


class EmployeeListView(PermissionRequiredMixin, EmployeeScopeMixin, ListView):
    permission_required = "employees.view_employee"
    template_name = "employees/employee_list.html"
    context_object_name = "employees"
    paginate_by = 10

    def get_queryset(self):
        # Scoped (and select_related) queryset from EmployeeScopeMixin.
        queryset = super().get_queryset().order_by("-date_hired", "last_name", "pk")

        # "john smith" must match first_name=John AND last_name=Smith, so
        # every word has to match at least one field (AND of ORs).
        for term in (self.request.GET.get("q") or "").split():
            queryset = queryset.filter(
                Q(first_name__icontains=term)
                | Q(last_name__icontains=term)
                | Q(email__icontains=term)
                | Q(job_title__icontains=term)
            )
        return queryset


class EmployeeDetailView(PermissionRequiredMixin, EmployeeScopeMixin, DetailView):
    permission_required = "employees.view_employee"
    template_name = "employees/employee_detail.html"
    context_object_name = "employee"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.object
        # Field-level security: the salary is only put in the context when
        # this user is allowed to see it, so it cannot leak via the template.
        if can_view_salary(self.request.user, employee):
            context["salary_cents"] = employee.salary_cents
        return context


class MyProfileView(View):
    """Shortcut to the logged-in user's own employee record."""

    def get(self, request):
        profile = getattr(request.user, "employee_profile", None)
        if profile is None:
            raise Http404("No employee profile is linked to this account.")
        return redirect("employee_detail", pk=profile.pk)


class EmployeeCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "employees.add_employee"
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/employee_form.html"
    success_url = reverse_lazy("employee_list")


class EmployeeUpdateView(PermissionRequiredMixin, EmployeeScopeMixin, UpdateView):
    permission_required = "employees.change_employee"
    form_class = EmployeeForm
    template_name = "employees/employee_form.html"
    success_url = reverse_lazy("employee_list")


class EmployeeDeleteView(PermissionRequiredMixin, EmployeeScopeMixin, DeleteView):
    permission_required = "employees.delete_employee"
    template_name = "employees/employee_confirm_delete.html"
    success_url = reverse_lazy("employee_list")


# ============ DEPARTMENT VIEWS ============


class DepartmentListView(PermissionRequiredMixin, ListView):
    permission_required = "employees.view_department"
    model = Department
    template_name = "employees/department_list.html"
    context_object_name = "departments"

    def get_queryset(self):
        return Department.objects.annotate(
            emp_count=Count("employees", filter=Q(employees__status__in=PAYABLE_STATUSES))
        ).order_by("name")


class DepartmentCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "employees.add_department"
    model = Department
    form_class = DepartmentForm
    template_name = "employees/department_form.html"
    success_url = reverse_lazy("department_list")


# ============ DASHBOARD REPORT ============


class DashboardView(PermissionRequiredMixin, TemplateView):
    permission_required = "employees.view_reports"
    template_name = "employees/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["summary"] = company_summary()  # 1 query
        context["departments"] = department_breakdown()  # 1 query
        return context


# ============ OPERATIONS ============


@login_not_required
def healthz(request):
    """Liveness + database check for Docker / load balancers. Public, reveals nothing."""
    try:
        connection.ensure_connection()
    except OperationalError:
        return JsonResponse({"status": "database unavailable"}, status=503)
    return JsonResponse({"status": "ok"})
