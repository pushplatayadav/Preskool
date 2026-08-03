"""Migration for the hrm LeaveRequest model."""
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hrm", "0004_leavetype"),
    ]

    operations = [
        migrations.CreateModel(
            name="LeaveRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("code", models.CharField(blank=True, max_length=20, unique=True)),
                ("applicant_name", models.CharField(max_length=100)),
                ("applicant_id", models.CharField(blank=True, max_length=50)),
                ("role", models.CharField(blank=True, max_length=50)),
                (
                    "leave_type",
                    models.CharField(
                        choices=[
                            ("medical", "Medical Leave"),
                            ("casual", "Casual Leave"),
                            ("maternity", "Maternity Leave"),
                            ("paternity", "Paternity Leave"),
                            ("sick", "Sick Leave"),
                            ("special", "Special Leave"),
                        ],
                        max_length=20,
                    ),
                ),
                ("from_date", models.DateField()),
                ("to_date", models.DateField()),
                ("no_of_days", models.IntegerField(default=1)),
                ("applied_on", models.DateField(default=django.utils.timezone.localdate)),
                ("authority", models.CharField(blank=True, max_length=100)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("approved", "Approved"),
                            ("disapproved", "Disapproved"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("reason", models.TextField(blank=True)),
                ("note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-applied_on", "-created_at"],
            },
        ),
    ]
