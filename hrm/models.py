from django.db import models
from django.utils import timezone


class Department(models.Model):
    code = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            max_suffix = 757238
            for dept in Department.objects.exclude(code="").exclude(pk=self.pk):
                try:
                    num = int(dept.code.replace("D", ""))
                    max_suffix = max(max_suffix, num)
                except (ValueError, AttributeError):
                    continue
            self.code = f"D{max_suffix + 1}"
        super().save(*args, **kwargs)


class Designation(models.Model):
    code = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            max_suffix = 748284
            for desig in Designation.objects.exclude(code="").exclude(pk=self.pk):
                try:
                    num = int(desig.code.replace("DS", ""))
                    max_suffix = max(max_suffix, num)
                except (ValueError, AttributeError):
                    continue
            self.code = f"DS{max_suffix + 1}"
        super().save(*args, **kwargs)


class Holiday(models.Model):
    code = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code:
            max_suffix = 752762
            for holiday in Holiday.objects.exclude(code="").exclude(pk=self.pk):
                try:
                    num = int(holiday.code.replace("H", ""))
                    max_suffix = max(max_suffix, num)
                except (ValueError, AttributeError):
                    continue
            self.code = f"H{max_suffix + 1}"
        super().save(*args, **kwargs)


class LeaveType(models.Model):
    code = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            max_suffix = 748294
            for leave in LeaveType.objects.exclude(code="").exclude(pk=self.pk):
                try:
                    num = int(leave.code.replace("LT", ""))
                    max_suffix = max(max_suffix, num)
                except (ValueError, AttributeError):
                    continue
            self.code = f"LT{max_suffix + 1}"
        super().save(*args, **kwargs)


class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ("medical", "Medical Leave"),
        ("casual", "Casual Leave"),
        ("maternity", "Maternity Leave"),
        ("paternity", "Paternity Leave"),
        ("sick", "Sick Leave"),
        ("special", "Special Leave"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("disapproved", "Disapproved"),
    ]

    code = models.CharField(max_length=20, unique=True, blank=True)
    applicant_name = models.CharField(max_length=100)
    applicant_id = models.CharField(max_length=50, blank=True)
    role = models.CharField(max_length=50, blank=True)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    from_date = models.DateField()
    to_date = models.DateField()
    no_of_days = models.IntegerField(default=1)
    applied_on = models.DateField(default=timezone.localdate)
    authority = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    reason = models.TextField(blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-applied_on", "-created_at"]

    def __str__(self):
        return f"{self.applicant_name} - {self.get_leave_type_display()} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.code:
            max_suffix = 757000
            for req in LeaveRequest.objects.exclude(code="").exclude(pk=self.pk):
                try:
                    num = int(req.code.replace("LR", ""))
                    max_suffix = max(max_suffix, num)
                except (ValueError, AttributeError):
                    continue
            self.code = f"LR{max_suffix + 1}"
        super().save(*args, **kwargs)


class Payroll(models.Model):
    PAYROLL_STATUS_CHOICES = [
        ("generated", "Generated"),
        ("paid", "Paid"),
        ("pending", "Pending"),
    ]

    code = models.CharField(max_length=20, unique=True, blank=True)
    teacher = models.ForeignKey(
        "people.Teacher", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="payrolls"
    )
    staff = models.ForeignKey(
        "people.Staff", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="payrolls"
    )
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    month = models.CharField(max_length=20, blank=True)
    year = models.CharField(max_length=10, blank=True)

    # Earnings
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    house_rent_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    dearness_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Deductions
    tax_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    provident_fund = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    insurance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20, choices=PAYROLL_STATUS_CHOICES, default="generated"
    )
    pay_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.code}"

    @property
    def total_earnings(self):
        return (
            self.basic_salary
            + self.house_rent_allowance
            + self.dearness_allowance
            + self.medical_allowance
            + self.other_allowance
            + self.bonus
        )

    @property
    def total_deductions(self):
        return (
            self.tax_deduction
            + self.provident_fund
            + self.insurance
            + self.other_deduction
        )

    def save(self, *args, **kwargs):
        if not self.code:
            max_suffix = 738197
            for pay in Payroll.objects.exclude(code="").exclude(pk=self.pk):
                try:
                    num = int(pay.code.replace("P", ""))
                    max_suffix = max(max_suffix, num)
                except (ValueError, AttributeError):
                    continue
            self.code = f"P{max_suffix + 1}"
        super().save(*args, **kwargs)
