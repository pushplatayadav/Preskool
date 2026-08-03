"""Migration for the hrm Holiday model."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hrm", "0002_designation"),
    ]

    operations = [
        migrations.CreateModel(
            name="Holiday",
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
                ("title", models.CharField(max_length=100)),
                ("date", models.DateField()),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["date"],
            },
        ),
    ]
