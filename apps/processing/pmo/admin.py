from .models import WatercourseStation, WatercourseObservation
from apps.common.actions import stream_as_csv_action
from apps.common.list_filter import DateRangeRangeFilter, ResultNullReasonFilter
from django.contrib import admin



class MeteoStationAdmin(admin.ModelAdmin):
    list_display = ['name', 'id_by_provider']
    fields = ['name','id_by_provider']


class WatercourseObservationAdmin(admin.ModelAdmin):
    actions = [
        stream_as_csv_action("CSV Export (stream)", fields=[
            'phenomenon_time_from',
            'phenomenon_time_duration',
            'observed_property',
            'feature_of_interest',
            'procedure',
            'result_for_human',
        ]),
    ]

    list_display = (
        'phenomenon_time_from',
        'phenomenon_time_duration_for_human',
        'observed_property',
        'feature_of_interest',
        'procedure',
        'result_for_human',
    )
    list_filter = (
        DateRangeRangeFilter,
        ('observed_property', admin.RelatedOnlyFieldListFilter),
        ('feature_of_interest', admin.RelatedOnlyFieldListFilter),
        ('procedure', admin.RelatedOnlyFieldListFilter),
        ('result_null_reason', ResultNullReasonFilter),
    )
    fields = list_display
    readonly_fields = fields


admin.site.register(WatercourseObservation, WatercourseObservationAdmin)
admin.site.register(WatercourseStation, MeteoStationAdmin)