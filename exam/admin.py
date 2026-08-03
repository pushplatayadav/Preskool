from django.contrib import admin
from .models import Exam, Grade, ExamSchedule, ExamAttendance, ExamResult


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("exam_id", "name", "school_class", "section", "subject", "exam_date", "status")
    list_filter = ("school_class", "section", "status")
    search_fields = ("exam_id", "name")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("name", "min_marks", "max_marks", "grade_point", "status")
    list_filter = ("status",)


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ("schedule_id", "exam", "school_class", "section", "subject", "exam_date", "status")
    list_filter = ("status",)


@admin.register(ExamAttendance)
class ExamAttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "status")
    list_filter = ("status",)


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "marks_obtained", "grade")
