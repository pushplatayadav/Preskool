from django.db import models
from django.conf import settings


class FeesGroup(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            max_suffix = 80480
            for fg in FeesGroup.objects.exclude(code="").exclude(pk=self.pk):
                try:
                    num = int(fg.code.replace("FG", ""))
                    max_suffix = max(max_suffix, num)
                except (ValueError, AttributeError):
                    continue
            self.code = f"FG{max_suffix + 1:05d}"
        super().save(*args, **kwargs)


class FeesType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, blank=True)
    fees_group = models.ForeignKey(
        FeesGroup, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="fees_types"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    @property
    def fees_code(self):
        return "-".join(part for part in self.name.split() if part)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            max_suffix = 80480
            for ft in FeesType.objects.exclude(code="").exclude(pk=self.pk):
                try:
                    num = int(ft.code.replace("FG", ""))
                    max_suffix = max(max_suffix, num)
                except (ValueError, AttributeError):
                    continue
            self.code = f"FG{max_suffix + 1:05d}"
        super().save(*args, **kwargs)


class Fees(models.Model):
    STATUS_CHOICES = [
        ("paid", "Paid"),
        ("unpaid", "Unpaid"),
        ("partial", "Partial"),
    ]
    PAYMENT_MODE_CHOICES = [
        ("cash", "Cash"),
        ("cheque", "Cheque"),
        ("online", "Online Transfer"),
        ("card", "Card"),
        ("paytm", "Paytm"),
        ("cod", "Cash On Delivery"),
    ]

    student = models.ForeignKey(
        "people.Student", on_delete=models.CASCADE, related_name="fees"
    )
    fees_group = models.ForeignKey(
        FeesGroup, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="fees"
    )
    fees_type = models.ForeignKey(
        FeesType, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="fees"
    )
    fees_code = models.CharField(max_length=100, blank=True)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="unpaid"
    )
    ref_id = models.CharField(max_length=50, blank=True)
    payment_mode = models.CharField(
        max_length=20, choices=PAYMENT_MODE_CHOICES, blank=True
    )
    date_paid = models.DateField(null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    academic_year = models.ForeignKey(
        "core.AcademicYear", on_delete=models.CASCADE,
        related_name="student_fees", null=True, blank=True
    )
    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="collected_fees"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Fees"

    def __str__(self):
        return f"{self.student.name} - {self.fees_group} ({self.amount})"


class FeesMaster(models.Model):
    FINE_TYPE_CHOICES = [
        ("none", "None"),
        ("percentage", "Percentage"),
        ("fixed", "Fixed"),
    ]

    code = models.CharField(max_length=20, unique=True, blank=True)
    fees_group = models.ForeignKey(
        FeesGroup, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="fees_masters"
    )
    fees_type = models.ForeignKey(
        FeesType, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="fees_masters"
    )
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fine_type = models.CharField(
        max_length=20, choices=FINE_TYPE_CHOICES, default="none"
    )
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Fees Masters"

    def __str__(self):
        return f"{self.code} - {self.fees_group} ({self.amount})"

    def save(self, *args, **kwargs):
        if not self.code:
            max_suffix = 80480
            for fm in FeesMaster.objects.exclude(code="").exclude(pk=self.pk):
                try:
                    num = int(fm.code.replace("FG", ""))
                    max_suffix = max(max_suffix, num)
                except (ValueError, AttributeError):
                    continue
            self.code = f"FG{max_suffix + 1:05d}"
        super().save(*args, **kwargs)


class FeesAssign(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("both", "Both"),
    ]

    fees_group = models.ForeignKey(
        FeesGroup, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="fees_assigns"
    )
    fees_type = models.ForeignKey(
        FeesType, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="fees_assigns"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    school_class = models.ForeignKey(
        "academics.SchoolClass", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="fees_assigns"
    )
    section = models.ForeignKey(
        "academics.Section", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="fees_assigns"
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    category = models.CharField(max_length=50, blank=True)
    academic_year = models.ForeignKey(
        "core.AcademicYear", on_delete=models.CASCADE,
        related_name="fees_assigns", null=True, blank=True
    )
    assigned_students = models.ManyToManyField(
        "people.Student", blank=True, related_name="fees_assigns"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Fees Assigns"

    def __str__(self):
        return f"{self.fees_group} - {self.fees_type} ({self.amount})"

    @property
    def gender_display(self):
        return self.get_gender_display() if self.gender else "-"

    @property
    def assigned_count(self):
        return self.assigned_students.count()
