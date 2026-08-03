from django.urls import path
from django.views.generic.base import RedirectView
from . import views

app_name = "people"

urlpatterns = [
    path("student-grid/", views.student_grid, name="student-grid"),
    path("student-grid/students.html", RedirectView.as_view(pattern_name="people:student-list", permanent=False), name="student-grid-to-list"),
    path("student-grid/<int:pk>/delete/", views.student_grid, name="student-grid-delete"),
    path("students/", views.student_list, name="student-list"),
    path("get-sections/", views.get_sections, name="get-sections"),
    path("add-student/", views.add_student_ajax, name="add-student"),
    path("add-student-page/", views.add_student_page, name="add-student-page"),
    path("edit-student/<int:pk>/", views.edit_student_page, name="edit-student"),
    path("student-details/", views.student_details_redirect, name="student-details-redirect"),
    path("student-details/<int:pk>/", views.student_details, name="student-details"),
    path("student-promotion/", views.student_promotion, name="student-promotion"),
    path("student-leaves/<int:pk>/", views.student_leaves, name="student-leaves"),
    path("student-attendance/", views.student_attendance_list, name="student-attendance"),
    path("student-attendance/save-ajax/", views.student_attendance_save_ajax, name="student-attendance-save-ajax"),
    path("student-attendance/export/pdf/", views.student_attendance_export_pdf, name="student-attendance-export-pdf"),
    path("student-attendance/export/excel/", views.student_attendance_export_excel, name="student-attendance-export-excel"),
    # Teacher Attendance URLs
    path("teacher-attendance/", views.teacher_attendance_list, name="teacher-attendance"),
    path("teacher-attendance/save-ajax/", views.teacher_attendance_save_ajax, name="teacher-attendance-save-ajax"),
    path("teacher-attendance/export/pdf/", views.teacher_attendance_export_pdf, name="teacher-attendance-export-pdf"),
    path("teacher-attendance/export/excel/", views.teacher_attendance_export_excel, name="teacher-attendance-export-excel"),
    # Teacher URLs
    path("teachers/", views.teacher_list, name="teacher-list"),
    path("teacher-grid/", views.teacher_grid, name="teacher-grid"),
    path("add-teacher/", views.add_teacher, name="add-teacher"),
    path("edit-teacher/<int:pk>/", views.edit_teacher, name="edit-teacher"),
    path("teacher-details/", views.teacher_details_redirect, name="teacher-details-redirect"),
    path("teacher-details/<int:pk>/", views.teacher_details, name="teacher-details"),
    path("teachers/export/pdf/", views.teacher_export_pdf, name="teacher-export-pdf"),
    path("teachers/export/excel/", views.teacher_export_excel, name="teacher-export-excel"),
    # Staff Attendance URLs
    path("staff-attendance/", views.staff_attendance_list, name="staff-attendance"),
    path("staff-attendance/save-ajax/", views.staff_attendance_save_ajax, name="staff-attendance-save-ajax"),
    path("staff-attendance/export/pdf/", views.staff_attendance_export_pdf, name="staff-attendance-export-pdf"),
    path("staff-attendance/export/excel/", views.staff_attendance_export_excel, name="staff-attendance-export-excel"),
    # Staff URLs
    path("staffs/", views.staff_list, name="staff-list"),
    path("add-staff/", views.add_staff, name="add-staff"),
    path("edit-staff/<int:pk>/", views.edit_staff, name="edit-staff"),
    path("staff-details/", views.staff_details_redirect, name="staff-details-redirect"),
    path("staff-details/<int:pk>/", views.staff_details, name="staff-details"),
    path("staffs/export/pdf/", views.staff_export_pdf, name="staff-export-pdf"),
    path("staffs/export/excel/", views.staff_export_excel, name="staff-export-excel"),
    # Parent URLs
    path("parents/", views.parent_list, name="parent-list"),
    # Guardian URLs
    path("guardians/", views.guardian_list, name="guardian-list"),
    # Attendance Report URLs
    path("attendance-report/", views.attendance_report, name="attendance-report"),
    path("attendance-report/export/pdf/", views.attendance_report_export_pdf, name="attendance-report-export-pdf"),
    path("attendance-report/export/excel/", views.attendance_report_export_excel, name="attendance-report-export-excel"),
]
