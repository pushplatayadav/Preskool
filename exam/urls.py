from django.urls import path
from . import views

app_name = "exam"

urlpatterns = [
    path("exams/", views.exam_list, name="exam-list"),
    path("exams/<int:pk>/edit/", views.exam_edit, name="exam-edit"),
    path("exams/<int:pk>/delete/", views.exam_delete, name="exam-delete"),
    path("grades/", views.grade_list, name="grade-list"),
    path("grades/<int:pk>/edit/", views.grade_edit, name="grade-edit"),
    path("grades/<int:pk>/delete/", views.grade_delete, name="grade-delete"),
    path("exam-schedules/", views.exam_schedule_list, name="exam-schedule-list"),
    path("exam-schedules/<int:pk>/edit/", views.exam_schedule_edit, name="exam-schedule-edit"),
    path("exam-schedules/<int:pk>/delete/", views.exam_schedule_delete, name="exam-schedule-delete"),
    path("exam-attendance/", views.exam_attendance_list, name="exam-attendance-list"),
    path("exam-attendance/save-ajax/", views.exam_attendance_save_ajax, name="exam-attendance-save-ajax"),
    path("exam-attendance/<int:pk>/edit/", views.exam_attendance_edit, name="exam-attendance-edit"),
    path("exam-attendance/<int:pk>/delete/", views.exam_attendance_delete, name="exam-attendance-delete"),
    path("exam-attendance/export/pdf/", views.exam_attendance_export_pdf, name="exam-attendance-export-pdf"),
    path("exam-attendance/export/excel/", views.exam_attendance_export_excel, name="exam-attendance-export-excel"),
    path("exam-results/", views.exam_results_list, name="exam-results-list"),
    path("exam-results/get-subjects/", views.exam_result_subjects, name="exam-result-get-subjects"),
    path("exam-results/export/pdf/", views.exam_results_export_pdf, name="exam-results-export-pdf"),
    path("exam-results/export/excel/", views.exam_results_export_excel, name="exam-results-export-excel"),
    path("exam-results/<int:pk>/edit/", views.exam_result_edit, name="exam-result-edit"),
    path("exam-results/<int:pk>/delete/", views.exam_result_delete, name="exam-result-delete"),
    path("student/<int:pk>/result/", views.student_result, name="student-result"),
]
