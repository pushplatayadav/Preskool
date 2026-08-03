from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0006_staff"),
    ]

    operations = [
        migrations.AddField(
            model_name="staff",
            name="role",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="staff",
            name="primary_contact_number",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="staff",
            name="permanent_address",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="staff",
            name="blood_group",
            field=models.CharField(blank=True, choices=[("A+", "A+"), ("A-", "A-"), ("B+", "B+"), ("B-", "B-"), ("AB+", "AB+"), ("AB-", "AB-"), ("O+", "O+"), ("O-", "O-")], max_length=10),
        ),
        migrations.AddField(
            model_name="staff",
            name="marital_status",
            field=models.CharField(blank=True, choices=[("single", "Single"), ("married", "Married")], max_length=10),
        ),
        migrations.AddField(
            model_name="staff",
            name="languages_known",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="staff",
            name="father_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="staff",
            name="mother_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="staff",
            name="epf_no",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="staff",
            name="basic_salary",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="staff",
            name="contract_type",
            field=models.CharField(blank=True, choices=[("permanent", "Permanent"), ("temporary", "Temporary")], max_length=20),
        ),
        migrations.AddField(
            model_name="staff",
            name="work_shift",
            field=models.CharField(blank=True, choices=[("morning", "Morning"), ("afternoon", "Afternoon")], max_length=20),
        ),
        migrations.AddField(
            model_name="staff",
            name="work_location",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="staff",
            name="medical_leaves",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="staff",
            name="casual_leaves",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="staff",
            name="maternity_leaves",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="staff",
            name="sick_leaves",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="staff",
            name="account_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="staff",
            name="account_number",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="staff",
            name="bank_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="staff",
            name="ifsc_code",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="staff",
            name="branch_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="staff",
            name="route",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="staff",
            name="vehicle_number",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="staff",
            name="pickup_point",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="staff",
            name="hostel",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="staff",
            name="room_no",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="staff",
            name="facebook",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="staff",
            name="twitter",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="staff",
            name="linkedin",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="staff",
            name="instagram",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="staff",
            name="resume",
            field=models.FileField(blank=True, null=True, upload_to="staff/documents/"),
        ),
        migrations.AddField(
            model_name="staff",
            name="joining_letter",
            field=models.FileField(blank=True, null=True, upload_to="staff/documents/"),
        ),
    ]
