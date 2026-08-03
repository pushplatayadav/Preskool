from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0006_homework'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schedule_id', models.CharField(editable=False, max_length=20, unique=True)),
                ('schedule_type', models.CharField(default='Class', max_length=50)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['start_time'],
            },
        ),
    ]
