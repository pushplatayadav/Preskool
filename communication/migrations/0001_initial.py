"""Initial migration for the communication NoticeBoard model."""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0002_user_is_email_verified_otpverification"),
    ]

    operations = [
        migrations.CreateModel(
            name="NoticeBoard",
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
                ("title", models.CharField(max_length=200)),
                ("notice_date", models.DateField()),
                (
                    "publish_on",
                    models.DateField(blank=True, null=True),
                ),
                (
                    "attachment",
                    models.FileField(blank=True, null=True, upload_to="notice_board/"),
                ),
                ("message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "added_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="notices",
                        to="accounts.user",
                    ),
                ),
                (
                    "message_to",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Roles this notice is published to.",
                        related_name="notices",
                        to="accounts.role",
                    ),
                ),
            ],
            options={
                "ordering": ["-notice_date", "-created_at"],
            },
        ),
    ]
