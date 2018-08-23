from .models import Property, Process, Topic
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


class TopicAdmin(admin.ModelAdmin):
    readonly_fields = (
        'name_id',
     )

admin.site.register(Property, PropertyAdmin)
admin.site.register(Process, ProcessAdmin)
admin.site.register(Topic, TopicAdmin)