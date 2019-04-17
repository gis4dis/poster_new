from apps.common.actions import stream_as_csv_action
from apps.common.list_filter import DateRangeRangeFilter, ResultNullReasonFilter
from apps.processing.o2.list_filter import AgeRangeFilter
from .models import Zsj, MobilityStream, \
    MobilityObservation, SocioDemoObservation
from django.contrib import admin


class MobilityStreamAdmin(admin.ModelAdmin):
    readonly_fields = (
        'src_zsj',
        'dst_zsj',
    )


class ZsjAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id_by_provider',
    )


class MobilityObservationAdmin(admin.ModelAdmin):
    actions = [
        stream_as_csv_action("CSV Export (stream)", fields=[
            'phenomenon_time_from',
            'phenomenon_time_duration',
            'observed_property',
            'feature_of_interest',
            'procedure',
            'src_occurrence_type',
            'dst_occurrence_type',
            'uniques_type',
            'result_for_human',
        ]),
    ]

    list_display = (
        'phenomenon_time_from',
        'time_slots',
        'observed_property',
        'feature_of_interest',
        'procedure',
        'src_occurrence_type',
        'dst_occurrence_type',
        'uniques_type',
        'result_for_human'
    )
    list_filter = (
        DateRangeRangeFilter,
        ('time_slots', admin.RelatedOnlyFieldListFilter),
        ('observed_property', admin.RelatedOnlyFieldListFilter),
        ('feature_of_interest', admin.RelatedOnlyFieldListFilter),
        ('procedure', admin.RelatedOnlyFieldListFilter),
        'src_occurrence_type',
        'dst_occurrence_type',
        'uniques_type',
        ('result_null_reason', ResultNullReasonFilter)
    )
    fields = list_display + ('phenomenon_time_duration_for_human', 'created_at', 'updated_at')
    readonly_fields = fields


class SocioDemoObservationAdmin(admin.ModelAdmin):
    actions = [
        stream_as_csv_action("CSV Export (stream)", fields=[
            'phenomenon_time_from',
            'phenomenon_time_duration',
            'observed_property',
            'feature_of_interest',
            'procedure',
            'age_for_human',
            'gender',
            'occurrence_type',
            'result_for_human',
        ]),
    ]

    list_display = (
        'phenomenon_time_from',
        'time_slots',
        'observed_property',
        'feature_of_interest',
        'procedure',
        'age_for_human',
        'gender',
        'occurrence_type',
        'result_for_human'
    )
    list_filter = (
        DateRangeRangeFilter,
        ('time_slots', admin.RelatedOnlyFieldListFilter),
        ('observed_property', admin.RelatedOnlyFieldListFilter),
        ('feature_of_interest', admin.RelatedOnlyFieldListFilter),
        ('procedure', admin.RelatedOnlyFieldListFilter),
        AgeRangeFilter,
        'gender',
        'occurrence_type',
        ('result_null_reason', ResultNullReasonFilter)
    )
    fields = list_display + ('phenomenon_time_duration_for_human', 'created_at', 'updated_at')
    readonly_fields = fields


admin.site.register(Zsj, ZsjAdmin)
admin.site.register(MobilityStream, MobilityStreamAdmin)
admin.site.register(MobilityObservation, MobilityObservationAdmin)
admin.site.register(SocioDemoObservation, SocioDemoObservationAdmin)
