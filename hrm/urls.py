from django.urls import path
from . import views

app_name = "hrm"

urlpatterns = [
    path("departments/", views.department_list, name="department-list"),
    path("departments/<int:pk>/edit/", views.department_edit, name="department-edit"),
    path("departments/<int:pk>/delete/", views.department_delete, name="department-delete"),
    path("designation/", views.designation_list, name="designation-list"),
    path("designation/<int:pk>/edit/", views.designation_edit, name="designation-edit"),
    path("designation/<int:pk>/delete/", views.designation_delete, name="designation-delete"),
    path("holidays/", views.holiday_list, name="holiday-list"),
    path("holidays/<int:pk>/edit/", views.holiday_edit, name="holiday-edit"),
    path("holidays/<int:pk>/delete/", views.holiday_delete, name="holiday-delete"),
    path("leaves/", views.leave_list, name="leave-list"),
    path("leaves/<int:pk>/edit/", views.leave_edit, name="leave-edit"),
    path("leaves/<int:pk>/delete/", views.leave_delete, name="leave-delete"),
    path("approve-request/", views.approve_request_list, name="approve-request-list"),
    path("approve-request/export/pdf/", views.approve_request_export_pdf, name="approve-request-export-pdf"),
    path("approve-request/export/excel/", views.approve_request_export_excel, name="approve-request-export-excel"),
    path("approve-request/<int:pk>/update/", views.approve_request_update, name="approve-request-update"),
    path("approve-request/<int:pk>/delete/", views.approve_request_delete, name="approve-request-delete"),
    path("payroll/", views.payroll_list, name="payroll-list"),
    path("payroll/export/pdf/", views.payroll_export_pdf, name="payroll-export-pdf"),
    path("payroll/export/excel/", views.payroll_export_excel, name="payroll-export-excel"),
    path("payroll/<int:pk>/payslip/", views.payroll_payslip, name="payroll-payslip"),
    path("payroll/<int:pk>/update/", views.payroll_update, name="payroll-update"),
    path("payroll/<int:pk>/delete/", views.payroll_delete, name="payroll-delete"),
]
