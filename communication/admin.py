from django.contrib import admin

from .models import Event, NoticeBoard


@admin.register(NoticeBoard)
class NoticeBoardAdmin(admin.ModelAdmin):
    list_display = ("title", "notice_date", "publish_on", "added_by", "created_at")
    list_filter = ("notice_date", "message_to")
    search_fields = ("title", "message")
    filter_horizontal = ("message_to",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "event_for", "start_date", "end_date", "added_by", "created_at")
    list_filter = ("category", "event_for", "start_date")
    search_fields = ("title", "message")
    filter_horizontal = ("classes", "sections", "roles", "teachers")

