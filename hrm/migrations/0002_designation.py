"""Migration for the hrm Designation model."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hrm", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Designation",
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
                    "code",
                    models.CharField(blank=True, max_length=20, unique=True),
                ),
                ("name", models.CharField(max_length=100)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
    ]
