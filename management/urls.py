from django.urls import path
from . import views

app_name = "management"

urlpatterns = [
    path("library-members/", views.library_members_list, name="library-members"),
    path("library-members/export/excel/", views.library_members_export_excel, name="library-members-export-excel"),
    path("library-members/export/pdf/", views.library_members_export_pdf, name="library-members-export-pdf"),

    path("library-books/", views.library_books_list, name="library-books"),
    path("library-books/export/excel/", views.library_books_export_excel, name="library-books-export-excel"),
    path("library-books/export/pdf/", views.library_books_export_pdf, name="library-books-export-pdf"),

    path("library-issue-book/", views.library_issue_book_list, name="library-issue-book"),
    path("library-issue-book/export/excel/", views.library_issue_book_export_excel, name="library-issue-book-export-excel"),
    path("library-issue-book/export/pdf/", views.library_issue_book_export_pdf, name="library-issue-book-export-pdf"),

    path("library-return/", views.library_return_list, name="library-return"),
    path("library-return/export/excel/", views.library_return_export_excel, name="library-return-export-excel"),
    path("library-return/export/pdf/", views.library_return_export_pdf, name="library-return-export-pdf"),

    path("sports/", views.sports_list, name="sports"),
    path("sports/export/excel/", views.sports_export_excel, name="sports-export-excel"),
    path("sports/export/pdf/", views.sports_export_pdf, name="sports-export-pdf"),

    path("players/", views.players_list, name="players"),
    path("players/export/excel/", views.players_export_excel, name="players-export-excel"),
    path("players/export/pdf/", views.players_export_pdf, name="players-export-pdf"),

    path("hostel-list/", views.hostel_list, name="hostel-list"),
    path("hostel-list/export/excel/", views.hostel_export_excel, name="hostel-export-excel"),
    path("hostel-list/export/pdf/", views.hostel_export_pdf, name="hostel-export-pdf"),

    path("hostel-rooms/", views.hostel_rooms_list, name="hostel-rooms"),
    path("hostel-rooms/export/excel/", views.hostel_rooms_export_excel, name="hostel-rooms-export-excel"),
    path("hostel-rooms/export/pdf/", views.hostel_rooms_export_pdf, name="hostel-rooms-export-pdf"),

    path("hostel-room-type/", views.hostel_room_type_list, name="hostel-room-type"),
    path("hostel-room-type/export/excel/", views.hostel_room_type_export_excel, name="hostel-room-type-export-excel"),
    path("hostel-room-type/export/pdf/", views.hostel_room_type_export_pdf, name="hostel-room-type-export-pdf"),

    path("transport-routes/", views.transport_routes_list, name="transport-routes"),
    path("transport-routes/next-id/", views.transport_routes_next_id, name="transport-routes-next-id"),
    path("transport-routes/export/excel/", views.transport_routes_export_excel, name="transport-routes-export-excel"),
    path("transport-routes/export/pdf/", views.transport_routes_export_pdf, name="transport-routes-export-pdf"),

    path("transport-pickup-points/", views.transport_pickup_points_list, name="transport-pickup-points"),
    path("transport-pickup-points/next-id/", views.transport_pickup_points_next_id, name="transport-pickup-points-next-id"),
    path("transport-pickup-points/export/excel/", views.transport_pickup_points_export_excel, name="transport-pickup-points-export-excel"),
    path("transport-pickup-points/export/pdf/", views.transport_pickup_points_export_pdf, name="transport-pickup-points-export-pdf"),

    path("transport-vehicle-drivers/", views.transport_vehicle_drivers_list, name="transport-vehicle-drivers"),
    path("transport-vehicle-drivers/next-id/", views.transport_vehicle_drivers_next_id, name="transport-vehicle-drivers-next-id"),
    path("transport-vehicle-drivers/export/excel/", views.transport_vehicle_drivers_export_excel, name="transport-vehicle-drivers-export-excel"),
    path("transport-vehicle-drivers/export/pdf/", views.transport_vehicle_drivers_export_pdf, name="transport-vehicle-drivers-export-pdf"),

    path("transport-vehicle/", views.transport_vehicles_list, name="transport-vehicle"),
    path("transport-vehicle/next-id/", views.transport_vehicles_next_id, name="transport-vehicle-next-id"),
    path("transport-vehicle/export/excel/", views.transport_vehicles_export_excel, name="transport-vehicle-export-excel"),
    path("transport-vehicle/export/pdf/", views.transport_vehicles_export_pdf, name="transport-vehicle-export-pdf"),

    path("transport-assign-vehicle/", views.transport_assign_vehicles_list, name="transport-assign-vehicle"),
    path("transport-assign-vehicle/next-id/", views.transport_assign_vehicles_next_id, name="transport-assign-vehicle-next-id"),
    path("transport-assign-vehicle/export/excel/", views.transport_assign_vehicles_export_excel, name="transport-assign-vehicle-export-excel"),
    path("transport-assign-vehicle/export/pdf/", views.transport_assign_vehicles_export_pdf, name="transport-assign-vehicle-export-pdf"),
]
