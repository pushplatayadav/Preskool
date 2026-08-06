import uuid
from django.db import models
from core.models import AcademicYear
from django.conf import settings


class Student(models.Model):
    GENDER_CHOICES = [("male", "Male"), ("female", "Female"), ("other", "Other")]
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]
    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"), ("A-", "A-"), ("B+", "B+"), ("B-", "B-"),
        ("AB+", "AB+"), ("AB-", "AB-"), ("O+", "O+"), ("O-", "O-"),
    ]

    admission_no = models.CharField(max_length=20, unique=True)
    roll_no = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=100)
    school_class = models.ForeignKey("academics.SchoolClass", on_delete=models.CASCADE, related_name="students")
    section = models.ForeignKey("academics.Section", on_delete=models.CASCADE, related_name="students")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="male")
    parent_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to="students/", blank=True, null=True)
    parent_image = models.ImageField(upload_to="parents/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="students", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Additional Personal Information
    admission_date = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, blank=True)
    house = models.CharField(max_length=50, blank=True)
    religion = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=50, blank=True)
    primary_contact_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    caste = models.CharField(max_length=50, blank=True)
    mother_tongue = models.CharField(max_length=50, blank=True)
    languages_known = models.CharField(max_length=200, blank=True)

    # Father's Information
    father_name = models.CharField(max_length=100, blank=True)
    father_email = models.EmailField(blank=True)
    father_phone = models.CharField(max_length=20, blank=True)
    father_occupation = models.CharField(max_length=100, blank=True)
    father_image = models.ImageField(upload_to="parents/", blank=True, null=True)

    # Mother's Information
    mother_name = models.CharField(max_length=100, blank=True)
    mother_email = models.EmailField(blank=True)
    mother_phone = models.CharField(max_length=20, blank=True)
    mother_occupation = models.CharField(max_length=100, blank=True)
    mother_image = models.ImageField(upload_to="parents/", blank=True, null=True)

    # Guardian Information
    guardian_is = models.CharField(max_length=20, blank=True)
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_relation = models.CharField(max_length=50, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    guardian_email = models.EmailField(blank=True)
    guardian_occupation = models.CharField(max_length=100, blank=True)
    guardian_address = models.TextField(blank=True)
    guardian_image = models.ImageField(upload_to="guardians/", blank=True, null=True)

    # Sibling Information
    has_sibling_in_school = models.BooleanField(default=False)
    sibling_name = models.CharField(max_length=100, blank=True)
    sibling_roll_no = models.CharField(max_length=20, blank=True)
    sibling_admission_no = models.CharField(max_length=20, blank=True)
    sibling_class = models.CharField(max_length=50, blank=True)

    # Address
    current_address = models.TextField(blank=True)
    permanent_address = models.TextField(blank=True)

    # Transport Information
    route = models.CharField(max_length=100, blank=True)
    vehicle_number = models.CharField(max_length=50, blank=True)
    pickup_point = models.CharField(max_length=100, blank=True)

    # Hostel Information
    hostel = models.CharField(max_length=100, blank=True)
    room_no = models.CharField(max_length=20, blank=True)

    # Documents
    medical_document = models.FileField(upload_to="documents/", blank=True, null=True)
    transfer_certificate = models.FileField(upload_to="documents/", blank=True, null=True)

    # Medical History
    medical_condition = models.CharField(max_length=50, blank=True)
    allergies = models.CharField(max_length=200, blank=True)
    medications = models.CharField(max_length=200, blank=True)

    # Previous School Details
    previous_school_name = models.CharField(max_length=200, blank=True)
    previous_school_address = models.TextField(blank=True)
    previous_school_other_details = models.TextField(blank=True)

    # Bank Details
    bank_name = models.CharField(max_length=100, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)
    ifsc_number = models.CharField(max_length=20, blank=True)

    # Other Information
    other_information = models.TextField(blank=True)

    class Meta:
        ordering = ["school_class__numeric_order", "section__name", "roll_no"]


class Teacher(models.Model):
    GENDER_CHOICES = [("male", "Male"), ("female", "Female"), ("other", "Other")]
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]
    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"), ("A-", "A-"), ("B+", "B+"), ("B-", "B-"),
        ("AB+", "AB+"), ("AB-", "AB-"), ("O+", "O+"), ("O-", "O-"),
    ]
    MARITAL_STATUS_CHOICES = [("single", "Single"), ("married", "Married")]
    CONTRACT_TYPE_CHOICES = [("permanent", "Permanent"), ("temporary", "Temporary")]
    WORK_SHIFT_CHOICES = [("morning", "Morning"), ("afternoon", "Afternoon")]

    teacher_id = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="teacher_profiles"
    )
    name = models.CharField(max_length=100)
    school_class = models.ForeignKey("academics.SchoolClass", on_delete=models.SET_NULL, null=True, blank=True, related_name="teachers")
    subject = models.ForeignKey("academics.Subject", on_delete=models.SET_NULL, null=True, blank=True, related_name="teachers")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    primary_contact_number = models.CharField(max_length=20, blank=True)
    date_of_join = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="male")
    date_of_birth = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to="teachers/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    address = models.TextField(blank=True)
    permanent_address = models.TextField(blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    experience = models.CharField(max_length=200, blank=True)

    # Personal Information
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, blank=True)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True)
    languages_known = models.CharField(max_length=200, blank=True)
    father_name = models.CharField(max_length=100, blank=True)
    mother_name = models.CharField(max_length=100, blank=True)
    pan_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    # Previous School Details
    previous_school = models.CharField(max_length=200, blank=True)
    previous_school_address = models.TextField(blank=True)
    previous_school_phone = models.CharField(max_length=20, blank=True)

    # Payroll
    epf_no = models.CharField(max_length=50, blank=True)
    basic_salary = models.CharField(max_length=50, blank=True)
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES, blank=True)
    work_shift = models.CharField(max_length=20, choices=WORK_SHIFT_CHOICES, blank=True)
    work_location = models.CharField(max_length=200, blank=True)
    date_of_leaving = models.DateField(null=True, blank=True)

    # Leaves
    medical_leaves = models.CharField(max_length=50, blank=True)
    casual_leaves = models.CharField(max_length=50, blank=True)
    maternity_leaves = models.CharField(max_length=50, blank=True)
    sick_leaves = models.CharField(max_length=50, blank=True)

    # Bank Details
    account_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)
    branch_name = models.CharField(max_length=100, blank=True)

    # Transport Information
    route = models.CharField(max_length=100, blank=True)
    vehicle_number = models.CharField(max_length=50, blank=True)
    pickup_point = models.CharField(max_length=100, blank=True)

    # Hostel Information
    hostel = models.CharField(max_length=100, blank=True)
    room_no = models.CharField(max_length=20, blank=True)

    # Social Media Links
    facebook = models.CharField(max_length=500, blank=True)
    instagram = models.CharField(max_length=500, blank=True)
    linkedin = models.CharField(max_length=500, blank=True)
    youtube = models.CharField(max_length=500, blank=True)
    twitter = models.CharField(max_length=500, blank=True)

    # Documents
    resume = models.FileField(upload_to="teachers/documents/", blank=True, null=True)
    joining_letter = models.FileField(upload_to="teachers/documents/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.teacher_id:
            prefix = "T"
            last = Teacher.objects.order_by("-pk").first()
            next_num = (last.pk + 1) if last else 1
            self.teacher_id = f"{prefix}{849127 - next_num + 1}"
        super().save(*args, **kwargs)


class Staff(models.Model):
    GENDER_CHOICES = [("male", "Male"), ("female", "Female"), ("other", "Other")]
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]
    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"), ("A-", "A-"), ("B+", "B+"), ("B-", "B-"),
        ("AB+", "AB+"), ("AB-", "AB-"), ("O+", "O+"), ("O-", "O-"),
    ]
    MARITAL_STATUS_CHOICES = [("single", "Single"), ("married", "Married")]
    CONTRACT_TYPE_CHOICES = [("permanent", "Permanent"), ("temporary", "Temporary")]
    WORK_SHIFT_CHOICES = [("morning", "Morning"), ("afternoon", "Afternoon")]

    staff_id = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="staff_profiles"
    )
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    primary_contact_number = models.CharField(max_length=20, blank=True)
    date_of_join = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="male")
    date_of_birth = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to="staff/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    address = models.TextField(blank=True)
    permanent_address = models.TextField(blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    experience = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    # Personal Information
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, blank=True)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True)
    languages_known = models.CharField(max_length=200, blank=True)
    father_name = models.CharField(max_length=100, blank=True)
    mother_name = models.CharField(max_length=100, blank=True)

    # Payroll
    epf_no = models.CharField(max_length=50, blank=True)
    basic_salary = models.CharField(max_length=50, blank=True)
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES, blank=True)
    work_shift = models.CharField(max_length=20, choices=WORK_SHIFT_CHOICES, blank=True)
    work_location = models.CharField(max_length=200, blank=True)

    # Leaves
    medical_leaves = models.CharField(max_length=50, blank=True)
    casual_leaves = models.CharField(max_length=50, blank=True)
    maternity_leaves = models.CharField(max_length=50, blank=True)
    sick_leaves = models.CharField(max_length=50, blank=True)

    # Bank Details
    account_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)
    branch_name = models.CharField(max_length=100, blank=True)

    # Transport Information
    route = models.CharField(max_length=100, blank=True)
    vehicle_number = models.CharField(max_length=50, blank=True)
    pickup_point = models.CharField(max_length=100, blank=True)

    # Hostel Information
    hostel = models.CharField(max_length=100, blank=True)
    room_no = models.CharField(max_length=20, blank=True)

    # Social Media Links
    facebook = models.CharField(max_length=500, blank=True)
    twitter = models.CharField(max_length=500, blank=True)
    linkedin = models.CharField(max_length=500, blank=True)
    instagram = models.CharField(max_length=500, blank=True)

    # Documents
    resume = models.FileField(upload_to="staff/documents/", blank=True, null=True)
    joining_letter = models.FileField(upload_to="staff/documents/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.staff_id:
            numbers = []
            for sid in Staff.objects.values_list("staff_id", flat=True):
                if sid and sid.startswith("S") and sid[1:].isdigit():
                    numbers.append(int(sid[1:]))
            candidate = max(numbers) + 1 if numbers else 849128
            while Staff.objects.filter(staff_id=f"S{candidate}").exists():
                candidate += 1
            self.staff_id = f"S{candidate}"
        super().save(*args, **kwargs)


class StudentLeave(models.Model):
    LEAVE_TYPE_CHOICES = [
        ("medical", "Medical Leave"),
        ("casual", "Casual Leave"),
        ("maternity", "Maternity Leave"),
        ("paternity", "Paternity Leave"),
        ("special", "Special Leave"),
    ]
    LEAVE_DAYS_TYPE_CHOICES = [
        ("full", "Full Day"),
        ("first_half", "First Half"),
        ("second_half", "Second Half"),
    ]
    LEAVE_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="leaves")
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    from_date = models.DateField()
    to_date = models.DateField()
    no_of_days = models.IntegerField(default=1)
    leave_days_type = models.CharField(max_length=20, choices=LEAVE_DAYS_TYPE_CHOICES, default="full")
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=LEAVE_STATUS_CHOICES, default="pending")
    applied_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-applied_on"]

    def __str__(self):
        return f"{self.student.name} - {self.get_leave_type_display()} ({self.get_status_display()})"


class StudentAttendance(models.Model):
    ATTENDANCE_STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("half_day", "Half Day"),
        ("holiday", "Holiday"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField()
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS_CHOICES)
    academic_year = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE, null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]
        unique_together = ["student", "date"]

    def __str__(self):
        return f"{self.student.name} - {self.date} ({self.get_status_display()})"


class TeacherAttendance(models.Model):
    ATTENDANCE_STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("half_day", "Half Day"),
        ("holiday", "Holiday"),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField()
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS_CHOICES)
    academic_year = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE, null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]
        unique_together = ["teacher", "date"]

    def __str__(self):
        return f"{self.teacher.name} - {self.date} ({self.get_status_display()})"


class StaffAttendance(models.Model):
    ATTENDANCE_STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("half_day", "Half Day"),
        ("holiday", "Holiday"),
    ]

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField()
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS_CHOICES)
    academic_year = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE, null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]
        unique_together = ["staff", "date"]

    def __str__(self):
        return f"{self.staff.name} - {self.date} ({self.get_status_display()})"
