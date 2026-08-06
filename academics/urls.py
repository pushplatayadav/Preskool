from django.urls import path
from . import views

app_name = "academics"

urlpatterns = [
    path("classes/", views.classes_list, name="class-list"),
    path("classes/<int:pk>/edit/", views.class_edit, name="class-edit"),
    path("classes/<int:pk>/delete/", views.class_delete, name="class-delete"),
    path("class-home-work/", views.homework_list, name="homework-list"),
    path("class-home-work/<int:pk>/edit/", views.homework_edit, name="homework-edit"),
    path("class-home-work/<int:pk>/delete/", views.homework_delete, name="homework-delete"),
    path("schedule-classes/", views.schedule_list, name="schedule-list"),
    path("schedule-classes/<int:pk>/edit/", views.schedule_edit, name="schedule-edit"),
    path("schedule-classes/<int:pk>/delete/", views.schedule_delete, name="schedule-delete"),
    path("schedule-classes/availability/", views.schedule_availability, name="schedule-availability"),
    path("class-room/", views.classroom_list, name="classroom-list"),
    path("class-room/<int:pk>/edit/", views.classroom_edit, name="classroom-edit"),
    path("class-room/<int:pk>/delete/", views.classroom_delete, name="classroom-delete"),
    path("class-routine/", views.class_routine_list, name="classroutine-list"),
    path("class-routine/<int:pk>/edit/", views.class_routine_edit, name="classroutine-edit"),
    path("class-routine/<int:pk>/delete/", views.class_routine_delete, name="classroutine-delete"),
    path("sections/", views.section_list, name="section-list"),
    path("sections/<int:pk>/edit/", views.section_edit, name="section-edit"),
    path("sections/<int:pk>/delete/", views.section_delete, name="section-delete"),
    path("subjects/", views.subject_list, name="subject-list"),
    path("subjects/<int:pk>/edit/", views.subject_edit, name="subject-edit"),
    path("subjects/<int:pk>/delete/", views.subject_delete, name="subject-delete"),
    path("class-syllabus/", views.syllabus_list, name="syllabus-list"),
    path("class-syllabus/<int:pk>/edit/", views.syllabus_edit, name="syllabus-edit"),
    path("class-syllabus/<int:pk>/delete/", views.syllabus_delete, name="syllabus-delete"),
    path("class-syllabus/export/", views.syllabus_export, name="syllabus-export"),
    path("class-time-table/", views.class_time_table, name="class-time-table"),
    path("student/<int:pk>/time-table/", views.student_time_table, name="student-time-table"),
    path("academic-reasons/", views.academic_reasons_list, name="academic-reasons"),
    path("academic-reasons/export/pdf/", views.academic_reasons_export_pdf, name="academic-reasons-export-pdf"),
    path("academic-reasons/export/excel/", views.academic_reasons_export_excel, name="academic-reasons-export-excel"),
]
