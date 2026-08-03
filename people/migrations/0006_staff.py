from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_is_email_verified_otpverification"),
        ("people", "0005_teacher_additional_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="Staff",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("staff_id", models.CharField(max_length=20, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("department", models.CharField(blank=True, max_length=100)),
                ("designation", models.CharField(blank=True, max_length=100)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("date_of_join", models.DateField(blank=True, null=True)),
                ("gender", models.CharField(choices=[("male", "Male"), ("female", "Female"), ("other", "Other")], default="male", max_length=10)),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("profile_image", models.ImageField(blank=True, null=True, upload_to="staff/")),
                ("status", models.CharField(choices=[("active", "Active"), ("inactive", "Inactive")], default="active", max_length=10)),
                ("address", models.TextField(blank=True)),
                ("qualification", models.CharField(blank=True, max_length=200)),
                ("experience", models.CharField(blank=True, max_length=200)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="staff_profiles", to="accounts.user")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
