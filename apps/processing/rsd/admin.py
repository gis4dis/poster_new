from apps.common.actions import stream_as_csv_action
from apps.common.list_filter import DateRangeRangeFilter
from .models import EventCategory, EventObservation, AdminUnit
from django.contrib import admin


class EventObservationAdmin(admin.ModelAdmin):
    list_display = ['id_by_provider', 'category','result']
    fields = ['id_by_provider', 'category','result']


class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'id_by_provider']
    fields = ['name','id_by_provider']


class AdminUnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'id_by_provider','level']
    fields = ['name','id_by_provider','level']

admin.site.register(EventObservation, EventObservationAdmin)
admin.site.register(EventCategory, EventCategoryAdmin)
admin.site.register(AdminUnit, AdminUnitAdmin)