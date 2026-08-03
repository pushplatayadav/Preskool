from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0004_teacher"),
    ]

    operations = [
        migrations.AddField(
            model_name="teacher",
            name="primary_contact_number",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="teacher",
            name="permanent_address",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="teacher",
            name="blood_group",
            field=models.CharField(
                blank=True,
                choices=[
                    ("A+", "A+"), ("A-", "A-"), ("B+", "B+"), ("B-", "B-"),
                    ("AB+", "AB+"), ("AB-", "AB-"), ("O+", "O+"), ("O-", "O-"),
                ],
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="teacher",
            name="marital_status",
            field=models.CharField(
                blank=True,
                choices=[("single", "Single"), ("married", "Married")],
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="teacher",
            name="languages_known",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="teacher",
            name="father_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="teacher",
            name="mother_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="teacher",
            name="pan_number",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="teacher",
            name="notes",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="teacher",
            name="previous_school",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="teacher",
            name="previous_school_address",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="teacher",
            name="previous_school_phone",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="teacher",
            name="epf_no",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="teacher",
            name="basic_salary",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="teacher",
            name="contract_type",
            field=models.CharField(
                blank=True,
                choices=[("permanent", "Permanent"), ("temporary", "Temporary")],
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="teacher",
            name="work_shift",
            field=models.CharField(
                blank=True,
                choices=[("morning", "Morning"), ("afternoon", "Afternoon")],
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="teacher",
            name="work_location",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="teacher",
            name="date_of_leaving",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="teacher",
            name="medical_leaves",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="teacher",
            name="casual_leaves",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="teacher",
            name="maternity_leaves",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="teacher",
            name="sick_leaves",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="teacher",
            name="account_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="teacher",
            name="account_number",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="teacher",
            name="bank_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="teacher",
            name="ifsc_code",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="teacher",
            name="branch_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="teacher",
            name="route",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="teacher",
            name="vehicle_number",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="teacher",
            name="pickup_point",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="teacher",
            name="hostel",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="teacher",
            name="room_no",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="teacher",
            name="facebook",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="teacher",
            name="instagram",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="teacher",
            name="linkedin",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="teacher",
            name="youtube",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="teacher",
            name="twitter",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="teacher",
            name="resume",
            field=models.FileField(blank=True, null=True, upload_to="teachers/documents/"),
        ),
        migrations.AddField(
            model_name="teacher",
            name="joining_letter",
            field=models.FileField(blank=True, null=True, upload_to="teachers/documents/"),
        ),
    ]
