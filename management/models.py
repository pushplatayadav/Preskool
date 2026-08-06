from datetime import date
from django.db import models
from django.conf import settings


class LibraryMember(models.Model):
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Inactive", "Inactive"),
    ]

    member_id = models.CharField(max_length=50, blank=True, default="")
    card_no = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="library_memberships"
    )
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, default="")
    mobile = models.CharField(max_length=30, blank=True, default="")
    date_of_join = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")
    avatar = models.ImageField(upload_to="library_members/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["card_no", "name"]
        verbose_name = "Library Member"
        verbose_name_plural = "Library Members"

    def __str__(self):
        return f"{self.name} ({self.member_id or self.card_no})"


class Book(models.Model):
    book_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    book_no = models.CharField(max_length=50)
    publisher = models.CharField(max_length=150, blank=True, default="")
    author = models.CharField(max_length=150, blank=True, default="")
    subject = models.CharField(max_length=100, blank=True, default="")
    rack_no = models.CharField(max_length=50, blank=True, default="")
    qty = models.PositiveIntegerField(default=1)
    available = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    post_date = models.DateField(default=date.today)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["book_no", "name"]
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return f"{self.name} ({self.book_no})"


class BookIssue(models.Model):
    STATUS_CHOICES = [
        ("Issued", "Issued"),
        ("Returned", "Returned"),
        ("Overdue", "Overdue"),
    ]

    issue_id = models.CharField(max_length=50, unique=True)
    member = models.ForeignKey(LibraryMember, on_delete=models.CASCADE, related_name="book_issues")
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True, related_name="issues")
    issue_date = models.DateField(default=date.today)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    books_issued_count = models.PositiveIntegerField(default=1)
    books_returned_count = models.PositiveIntegerField(default=0)
    remarks = models.CharField(max_length=255, blank=True, default="Book Issued")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Issued")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issue_date", "issue_id"]
        verbose_name = "Book Issue"
        verbose_name_plural = "Book Issues"

    def __str__(self):
        return f"{self.issue_id} - {self.member.name}"


class BookReturn(models.Model):
    STATUS_CHOICES = [
        ("Returned", "Returned"),
        ("Partial Return", "Partial Return"),
        ("Overdue Return", "Overdue Return"),
    ]

    return_id = models.CharField(max_length=50, unique=True)
    issue = models.ForeignKey(BookIssue, on_delete=models.SET_NULL, null=True, blank=True, related_name="returns")
    member = models.ForeignKey(LibraryMember, on_delete=models.CASCADE, related_name="book_returns")
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True, related_name="returns")
    issue_date = models.DateField(default=date.today)
    due_date = models.DateField()
    return_date = models.DateField(default=date.today)
    books_issued_count = models.PositiveIntegerField(default=1)
    books_returned_count = models.PositiveIntegerField(default=1)
    remarks = models.CharField(max_length=255, blank=True, default="Book Returned")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Returned")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-return_date", "return_id"]
        verbose_name = "Book Return"
        verbose_name_plural = "Book Returns"

    def __str__(self):
        return f"{self.return_id} - {self.member.name}"


class Sport(models.Model):
    sport_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    coach = models.CharField(max_length=150, blank=True, default="")
    coach_avatar = models.ImageField(upload_to="sports_coaches/", blank=True, null=True)
    started_year = models.CharField(max_length=10, blank=True, default="2024")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sport_id", "name"]
        verbose_name = "Sport"
        verbose_name_plural = "Sports"

    def __str__(self):
        return f"{self.name} ({self.sport_id})"


class Player(models.Model):
    player_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True, blank=True, related_name="players")
    date_of_join = models.DateField(default=date.today)
    avatar = models.ImageField(upload_to="players/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["player_id", "name"]
        verbose_name = "Player"
        verbose_name_plural = "Players"

    def __str__(self):
        return f"{self.name} ({self.player_id})"


class Hostel(models.Model):
    HOSTEL_TYPE_CHOICES = [
        ("Boys", "Boys"),
        ("Girls", "Girls"),
        ("Combined", "Combined"),
    ]

    hostel_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    hostel_type = models.CharField(max_length=20, choices=HOSTEL_TYPE_CHOICES, default="Boys")
    address = models.CharField(max_length=255, blank=True, default="")
    intake = models.PositiveIntegerField(default=100)
    description = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["hostel_id", "name"]
        verbose_name = "Hostel"
        verbose_name_plural = "Hostels"

    def __str__(self):
        return f"{self.name} ({self.hostel_id})"


class HostelRoom(models.Model):
    ROOM_TYPE_CHOICES = [
        ("One Bed", "One Bed"),
        ("One Bed AC", "One Bed AC"),
        ("Two Bed", "Two Bed"),
        ("Two Bed AC", "Two Bed AC"),
        ("Three Bed", "Three Bed"),
        ("Four Bed", "Four Bed"),
    ]

    room_id = models.CharField(max_length=50, unique=True)
    room_no = models.CharField(max_length=50)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="rooms")
    room_type = models.CharField(max_length=50, choices=ROOM_TYPE_CHOICES, default="One Bed")
    no_of_beds = models.PositiveIntegerField(default=1)
    cost_per_bed = models.DecimalField(max_digits=10, decimal_places=2, default=200.00)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["room_id", "room_no"]
        verbose_name = "Hostel Room"
        verbose_name_plural = "Hostel Rooms"

    def __str__(self):
        return f"{self.room_no} - {self.hostel.name} ({self.room_id})"


class HostelRoomType(models.Model):
    type_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["type_id", "name"]
        verbose_name = "Hostel Room Type"
        verbose_name_plural = "Hostel Room Types"

    def __str__(self):
        return f"{self.name} ({self.type_id})"


class TransportRoute(models.Model):
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Inactive", "Inactive"),
    ]

    route_id = models.CharField(max_length=50, unique=True)
    route_name = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["route_id", "route_name"]
        verbose_name = "Transport Route"
        verbose_name_plural = "Transport Routes"

    def __str__(self):
        return f"{self.route_name} ({self.route_id})"


class TransportPickupPoint(models.Model):
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Inactive", "Inactive"),
    ]

    pickup_point_id = models.CharField(max_length=50, unique=True)
    pickup_point = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["pickup_point_id", "pickup_point"]
        verbose_name = "Transport Pickup Point"
        verbose_name_plural = "Transport Pickup Points"

    def __str__(self):
        return f"{self.pickup_point} ({self.pickup_point_id})"


class TransportVehicleDriver(models.Model):
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Inactive", "Inactive"),
    ]

    driver_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=30, blank=True, default="")
    driver_license_no = models.CharField(max_length=50, blank=True, default="")
    address = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "driver_id"]
        verbose_name = "Transport Vehicle Driver"
        verbose_name_plural = "Transport Vehicle Drivers"

    def __str__(self):
        return f"{self.name} ({self.driver_id})"


class TransportVehicle(models.Model):
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Inactive", "Inactive"),
    ]

    vehicle_id = models.CharField(max_length=50, unique=True)
    vehicle_no = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=150, blank=True, default="")
    made_of_year = models.CharField(max_length=10, blank=True, default="")
    registration_no = models.CharField(max_length=50, blank=True, default="")
    chassis_no = models.CharField(max_length=50, blank=True, default="")
    seat_capacity = models.PositiveIntegerField(default=1)
    gps_device_id = models.CharField(max_length=50, blank=True, default="")
    driver = models.ForeignKey(
        TransportVehicleDriver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicles",
    )
    driver_license_no = models.CharField(max_length=50, blank=True, default="")
    driver_contact_no = models.CharField(max_length=30, blank=True, default="")
    driver_address = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "vehicle_id"]
        verbose_name = "Transport Vehicle"
        verbose_name_plural = "Transport Vehicles"

    def __str__(self):
        return f"{self.vehicle_no} ({self.vehicle_id})"


class TransportAssignVehicle(models.Model):
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Inactive", "Inactive"),
    ]

    assign_id = models.CharField(max_length=50, unique=True)
    route = models.ForeignKey(
        TransportRoute,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assign_vehicles",
    )
    pickup_point = models.ForeignKey(
        TransportPickupPoint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assign_vehicles",
    )
    vehicle = models.ForeignKey(
        TransportVehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "assign_id"]
        verbose_name = "Transport Assign Vehicle"
        verbose_name_plural = "Transport Assign Vehicles"

    def __str__(self):
        return f"{self.assign_id} - {self.vehicle.vehicle_no if self.vehicle else '-'}"

