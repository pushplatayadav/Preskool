from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0003_section_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='no_of_students',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='section',
            name='no_of_subjects',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
