from django.urls import path
from . import views

app_name = "report"

urlpatterns = [
    path("class-report/", views.class_report, name="class-report"),
    path("class-report/<int:pk>/students/", views.class_report_students, name="class-report-students"),
    path("class-report/export/pdf/", views.class_report_export_pdf, name="class-report-export-pdf"),
    path("class-report/export/excel/", views.class_report_export_excel, name="class-report-export-excel"),
    path("student-report/", views.student_report, name="student-report"),
    path("student-report/export/pdf/", views.student_report_export_pdf, name="student-report-export-pdf"),
    path("student-report/export/excel/", views.student_report_export_excel, name="student-report-export-excel"),
    path("grade-report/", views.grade_report, name="grade-report"),
    path("grade-report/export/pdf/", views.grade_report_export_pdf, name="grade-report-export-pdf"),
    path("grade-report/export/excel/", views.grade_report_export_excel, name="grade-report-export-excel"),
    path("leave-report/", views.leave_report, name="leave-report"),
    path("leave-report/export/pdf/", views.leave_report_export_pdf, name="leave-report-export-pdf"),
    path("leave-report/export/excel/", views.leave_report_export_excel, name="leave-report-export-excel"),
    path("fees-report/", views.fees_report, name="fees-report"),
    path("fees-report/export/pdf/", views.fees_report_export_pdf, name="fees-report-export-pdf"),
    path("fees-report/export/excel/", views.fees_report_export_excel, name="fees-report-export-excel"),
]
