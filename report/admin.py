from django.contrib import admin
from .models import ClassReport, StudentReport


@admin.register(ClassReport)
class ClassReportAdmin(admin.ModelAdmin):
    list_display = ("display_id", "school_class", "section", "no_of_students", "report_date", "created_at")
    list_filter = ("school_class", "section", "report_date")
    search_fields = ("school_class__name", "section__name", "remarks")
    ordering = ("-created_at",)


@admin.register(StudentReport)
class StudentReportAdmin(admin.ModelAdmin):
    list_display = ("display_id", "student", "roll_no", "report_date", "created_at")
    list_filter = ("report_date",)
    search_fields = ("student__name", "student__admission_no", "remarks")
    ordering = ("-created_at",)
