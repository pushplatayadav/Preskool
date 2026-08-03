"""Create FeesMaster model."""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("fees", "0003_feestype_code_feestype_fees_group_feestype_is_active"),
    ]

    operations = [
        migrations.CreateModel(
            name="FeesMaster",
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
                ("due_date", models.DateField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "fine_type",
                    models.CharField(
                        choices=[
                            ("none", "None"),
                            ("percentage", "Percentage"),
                            ("fixed", "Fixed"),
                        ],
                        default="none",
                        max_length=20,
                    ),
                ),
                (
                    "fine_amount",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "fees_group",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="fees_masters",
                        to="fees.feesgroup",
                    ),
                ),
                (
                    "fees_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="fees_masters",
                        to="fees.feestype",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Fees Masters",
                "ordering": ["-created_at"],
            },
        ),
    ]
