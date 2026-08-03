from django.contrib import admin
from .models import FeesGroup, FeesType, FeesMaster, FeesAssign

admin.site.register(FeesGroup)
admin.site.register(FeesType)
admin.site.register(FeesMaster)
admin.site.register(FeesAssign)

