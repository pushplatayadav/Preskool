from django.urls import path
from . import views

app_name = "communication"

urlpatterns = [
    path("notice-board/", views.notice_board_list, name="notice-board"),
    path("notice-board/<int:pk>/edit/", views.notice_board_edit, name="notice-board-edit"),
    path("notice-board/<int:pk>/delete/", views.notice_board_delete, name="notice-board-delete"),
    path("notice-board/export/pdf/", views.notice_board_export_pdf, name="notice-board-export-pdf"),
    path("notice-board/export/excel/", views.notice_board_export_excel, name="notice-board-export-excel"),
    path("events/", views.events_list, name="events"),
    path("events/<int:pk>/edit/", views.events_edit, name="events-edit"),
    path("events/<int:pk>/delete/", views.events_delete, name="events-delete"),
    path("events/export/pdf/", views.events_export_pdf, name="events-export-pdf"),
    path("events/export/excel/", views.events_export_excel, name="events-export-excel"),
]
