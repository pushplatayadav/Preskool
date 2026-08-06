from django.contrib import admin
from .models import SchoolClass, Section, Subject, ClassRoom, Syllabus, TimeTableEntry, HomeWork, Schedule, AcademicReason


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_year", "numeric_order")
    list_filter = ("academic_year",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("school_class", "name", "no_of_students", "no_of_subjects", "is_active")
    list_filter = ("school_class", "is_active")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "academic_year", "type")
    list_filter = ("academic_year", "type")


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ("name", "room_number", "capacity", "floor")


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    list_display = ("title", "school_class", "subject", "uploaded_at")


@admin.register(TimeTableEntry)
class TimeTableEntryAdmin(admin.ModelAdmin):
    list_display = ("school_class", "section", "subject", "teacher", "day", "start_time", "end_time")
    list_filter = ("day", "school_class")


@admin.register(HomeWork)
class HomeWorkAdmin(admin.ModelAdmin):
    list_display = ("homework_id", "school_class", "section", "subject", "homework_date", "submission_date", "status", "created_by")
    list_filter = ("school_class", "section", "subject", "status")
    search_fields = ("homework_id",)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("schedule_id", "schedule_type", "start_time", "end_time", "status")
    list_filter = ("status",)
    search_fields = ("schedule_id",)


@admin.register(AcademicReason)
class AcademicReasonAdmin(admin.ModelAdmin):
    list_display = ("reason", "role", "status", "created_at")
    list_filter = ("role", "status")
    search_fields = ("reason",)

