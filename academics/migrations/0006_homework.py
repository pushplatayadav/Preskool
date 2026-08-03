import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0005_alter_classroom_id_alter_schoolclass_id_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HomeWork',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('homework_id', models.CharField(editable=False, max_length=20, unique=True)),
                ('homework_date', models.DateField()),
                ('submission_date', models.DateField()),
                ('attachments', models.FileField(blank=True, null=True, upload_to='homework/attachments/')),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='homeworks_created', to=settings.AUTH_USER_MODEL)),
                ('school_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='homeworks', to='academics.schoolclass')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='homeworks', to='academics.section')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='homeworks', to='academics.subject')),
            ],
            options={
                'ordering': ['-homework_date', '-created_at'],
            },
        ),
    ]
