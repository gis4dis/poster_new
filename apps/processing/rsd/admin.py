from apps.common.actions import stream_as_csv_action
from apps.common.list_filter import DateRangeRangeFilter
from .models import EventCategory
from django.contrib import admin


class EventCategoryAdmin(admin.ModelAdmin):
    readonly_fields = (
        'category',
    )


# admin.site.register(EventCategory, EventCategoryAdmin)
# admin.site.register(Observation, ObservationAdmin)