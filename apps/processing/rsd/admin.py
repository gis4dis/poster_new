from apps.common.actions import stream_as_csv_action
from apps.common.list_filter import DateRangeRangeFilter
from .models import EventCategory, EventObservation
from django.contrib import admin


class EventObservationAdmin(admin.ModelAdmin):
    list_display = ['id_by_provider', 'category','result']
    fields = ['id_by_provider', 'category','result']

admin.site.register(EventObservation, EventObservationAdmin)