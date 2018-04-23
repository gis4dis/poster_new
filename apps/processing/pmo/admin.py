from .models import MeteoStation
from django.contrib import admin


class MeteoStationAdmin(admin.ModelAdmin):
    list_display = ['name', 'id_by_provider']
    fields = ['name','id_by_provider']


admin.site.register(MeteoStation, MeteoStationAdmin)