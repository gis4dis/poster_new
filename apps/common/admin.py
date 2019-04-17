from .models import Property, Process, Topic, TimeSlots
from django.contrib import admin


class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'unit',
    )
    readonly_fields = (
        'name_id',
        'default_mean',
    )
    fields = (
        'name',
        'name_id',
        'unit',
        'default_mean',
    )


class ProcessAdmin(admin.ModelAdmin):
    readonly_fields = (
        'name_id',
    )

class TimeSlotAdmin(admin.ModelAdmin):
    readonly_fields = (
        'name_id',
        'zero',
        'frequency',
        'range_from',
        'range_to'
    )


class TopicAdmin(admin.ModelAdmin):
    pass

admin.site.register(Property, PropertyAdmin)
admin.site.register(Process, ProcessAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(TimeSlots, TimeSlotAdmin)