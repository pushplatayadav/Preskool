"""Create FeesAssign model."""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("academics", "0015_alter_examattendance_student_and_more"),
        ("core", "0003_alter_academicyear_id_alter_school_id"),
        ("people", "0009_staffattendance"),
        ("fees", "0004_feesmaster"),
    ]

    operations = [
        migrations.CreateModel(
            name="FeesAssign",
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
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=10
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("male", "Male"),
                            ("female", "Female"),
                            ("both", "Both"),
                        ],
                        max_length=10,
                    ),
                ),
                ("category", models.CharField(blank=True, max_length=50)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "academic_year",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fees_assigns",
                        to="core.academicyear",
                    ),
                ),
                (
                    "fees_group",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="fees_assigns",
                        to="fees.feesgroup",
                    ),
                ),
                (
                    "fees_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="fees_assigns",
                        to="fees.feestype",
                    ),
                ),
                (
                    "school_class",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="fees_assigns",
                        to="academics.schoolclass",
                    ),
                ),
                (
                    "section",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="fees_assigns",
                        to="academics.section",
                    ),
                ),
                (
                    "assigned_students",
                    models.ManyToManyField(
                        blank=True,
                        related_name="fees_assigns",
                        to="people.student",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Fees Assigns",
                "ordering": ["-created_at"],
            },
        ),
    ]
