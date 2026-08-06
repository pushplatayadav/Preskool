"""Migration for the hrm Payroll model."""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hrm", "0010_remove_seeded_leaverrequests"),
        ("people", "0009_staffattendance"),
    ]

    operations = [
        migrations.CreateModel(
            name="Payroll",
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
                (
                    "teacher",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="payrolls",
                        to="people.teacher",
                    ),
                ),
                (
                    "staff",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="payrolls",
                        to="people.staff",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("department", models.CharField(blank=True, max_length=100)),
                ("designation", models.CharField(blank=True, max_length=100)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("month", models.CharField(blank=True, max_length=20)),
                ("year", models.CharField(blank=True, max_length=10)),
                (
                    "basic_salary",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
                (
                    "house_rent_allowance",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
                (
                    "dearness_allowance",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
                (
                    "medical_allowance",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
                (
                    "other_allowance",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
                (
                    "bonus",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
                (
                    "tax_deduction",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
                (
                    "provident_fund",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
                (
                    "insurance",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
                (
                    "other_deduction",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
                (
                    "net_salary",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("generated", "Generated"),
                            ("paid", "Paid"),
                            ("pending", "Pending"),
                        ],
                        default="generated",
                        max_length=20,
                    ),
                ),
                ("pay_date", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
