from django.contrib import admin

from .models import Department, Designation, Holiday, LeaveRequest, LeaveType, Payroll


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name")


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name")


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "date", "description", "is_active", "created_at")
    list_filter = ("is_active", "date")
    search_fields = ("code", "title", "description")


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name")


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "applicant_name",
        "applicant_id",
        "leave_type",
        "from_date",
        "to_date",
        "no_of_days",
        "status",
        "authority",
        "applied_on",
    )
    list_filter = ("status", "leave_type", "role")
    search_fields = ("code", "applicant_name", "applicant_id", "authority")
    list_per_page = 20


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "department",
        "designation",
        "month",
        "year",
        "net_salary",
        "status",
        "pay_date",
    )
    list_filter = ("status", "month", "year")
    search_fields = ("code", "name", "department", "designation", "phone")
    readonly_fields = ("net_salary",)
    list_per_page = 20
