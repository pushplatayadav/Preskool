from django.contrib import admin

from .models import LibraryMember, Book, BookIssue, BookReturn, Sport, Player, Hostel, HostelRoom, HostelRoomType, TransportRoute, TransportPickupPoint, TransportVehicleDriver, TransportVehicle, TransportAssignVehicle



@admin.register(TransportRoute)
class TransportRouteAdmin(admin.ModelAdmin):
    list_display = ("route_id", "route_name", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("route_id", "route_name")
    ordering = ("route_name",)


@admin.register(TransportPickupPoint)
class TransportPickupPointAdmin(admin.ModelAdmin):
    list_display = ("pickup_point_id", "pickup_point", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("pickup_point_id", "pickup_point")
    ordering = ("pickup_point",)


@admin.register(TransportVehicleDriver)
class TransportVehicleDriverAdmin(admin.ModelAdmin):
    list_display = ("driver_id", "name", "phone_number", "driver_license_no", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("driver_id", "name", "phone_number", "driver_license_no", "address")
    ordering = ("name",)


@admin.register(TransportVehicle)
class TransportVehicleAdmin(admin.ModelAdmin):
    list_display = ("vehicle_id", "vehicle_no", "vehicle_model", "made_of_year", "registration_no", "gps_device_id", "driver", "status", "created_at")
    list_filter = ("status", "vehicle_model")
    search_fields = ("vehicle_id", "vehicle_no", "vehicle_model", "registration_no", "chassis_no", "gps_device_id", "driver__name")
    ordering = ("vehicle_no",)


@admin.register(TransportAssignVehicle)
class TransportAssignVehicleAdmin(admin.ModelAdmin):
    list_display = ("assign_id", "route", "pickup_point", "vehicle", "status", "created_at")
    list_filter = ("status", "route")
    search_fields = ("assign_id", "route__route_name", "pickup_point__pickup_point", "vehicle__vehicle_no", "vehicle__driver__name")
    ordering = ("assign_id",)
