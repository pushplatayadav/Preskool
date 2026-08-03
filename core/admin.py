from django.contrib import admin
from .models import School, AcademicYear   # drop School if not using it

admin.site.register(School)
admin.site.register(AcademicYear)
