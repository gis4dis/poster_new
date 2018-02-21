from apps.common.actions import stream_as_csv_action
from apps.common.list_filter import DateRangeRangeFilter
# from .models import SamplingFeature, Observation
from django.contrib import admin


class SamplingFeatureAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id_by_provider',
    )


class ObservationAdmin(admin.ModelAdmin):
    actions = [
        stream_as_csv_action("CSV Export (stream)", fields=[
            'phenomenon_time_from', 'phenomenon_time_duration', 'observed_property', 'feature_of_interest', 'procedure', 'result',
        ]),
    ]

    list_display = (
        'phenomenon_time_from',
        'phenomenon_time_duration_for_human',
        'observed_property',
        'feature_of_interest',
        'procedure',
        'result',
    )
    list_filter = (
        DateRangeRangeFilter,
        ('observed_property', admin.RelatedOnlyFieldListFilter),
        ('feature_of_interest', admin.RelatedOnlyFieldListFilter),
        ('procedure', admin.RelatedOnlyFieldListFilter),
        'result_null_reason',
    )
    fields = (
        'phenomenon_time_from',
        'phenomenon_time_duration_for_human',
        'observed_property',
        'feature_of_interest',
        'procedure',
        'related_observations',
        'result',
        'result_null_reason',
    )
    readonly_fields = (
        'phenomenon_time_from',
        'phenomenon_time_duration_for_human',
        'observed_property',
        'feature_of_interest',
        'procedure',
        'related_observations',
        'result',
        'result_null_reason',
    )


# admin.site.register(SamplingFeature, SamplingFeatureAdmin)
# admin.site.register(Observation, ObservationAdmin)