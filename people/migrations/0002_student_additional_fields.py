from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='admission_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='blood_group',
            field=models.CharField(blank=True, choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], max_length=10),
        ),
        migrations.AddField(
            model_name='student',
            name='house',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='student',
            name='religion',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='student',
            name='category',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='student',
            name='primary_contact_number',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='student',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='student',
            name='caste',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='student',
            name='mother_tongue',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='student',
            name='languages_known',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='student',
            name='father_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='student',
            name='father_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='student',
            name='father_phone',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='student',
            name='father_occupation',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='student',
            name='father_image',
            field=models.ImageField(blank=True, null=True, upload_to='parents/'),
        ),
        migrations.AddField(
            model_name='student',
            name='mother_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='student',
            name='mother_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='student',
            name='mother_phone',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='student',
            name='mother_occupation',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='student',
            name='mother_image',
            field=models.ImageField(blank=True, null=True, upload_to='parents/'),
        ),
        migrations.AddField(
            model_name='student',
            name='guardian_is',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='student',
            name='guardian_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='student',
            name='guardian_relation',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='student',
            name='guardian_phone',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='student',
            name='guardian_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='student',
            name='guardian_occupation',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='student',
            name='guardian_address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='student',
            name='guardian_image',
            field=models.ImageField(blank=True, null=True, upload_to='guardians/'),
        ),
        migrations.AddField(
            model_name='student',
            name='has_sibling_in_school',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='student',
            name='sibling_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='student',
            name='sibling_roll_no',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='student',
            name='sibling_admission_no',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='student',
            name='sibling_class',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='student',
            name='current_address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='student',
            name='permanent_address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='student',
            name='route',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='student',
            name='vehicle_number',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='student',
            name='pickup_point',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='student',
            name='hostel',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='student',
            name='room_no',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='student',
            name='medical_document',
            field=models.FileField(blank=True, null=True, upload_to='documents/'),
        ),
        migrations.AddField(
            model_name='student',
            name='transfer_certificate',
            field=models.FileField(blank=True, null=True, upload_to='documents/'),
        ),
        migrations.AddField(
            model_name='student',
            name='medical_condition',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='student',
            name='allergies',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='student',
            name='medications',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='student',
            name='previous_school_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='student',
            name='previous_school_address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='student',
            name='previous_school_other_details',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='student',
            name='bank_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='student',
            name='bank_branch',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='student',
            name='ifsc_number',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='student',
            name='other_information',
            field=models.TextField(blank=True),
        ),
    ]
