from django.contrib.gis.db import models
from apps.common.models import AbstractFeature, AbstractObservation


class SamplingFeature(AbstractFeature):
    geometry = models.PointField(
        help_text="Spatial information about feature.",
        srid=3857,
        null=True,
    )


class Observation(AbstractObservation):
    # TODO: migrate this to general Observation model

    # NOTE: see parent class for more information
    feature_of_interest = models.ForeignKey(
        SamplingFeature,
        help_text="Weather station where the observation was taken.",
        related_name='observations',
        editable=False,
        on_delete=models.DO_NOTHING
    )

    class Meta:
        get_latest_by = 'phenomenon_time_range'
        ordering = ['-phenomenon_time_range', 'feature_of_interest', 'procedure',
                    'observed_property']
        '''
        unique_together = (('phenomenon_time_range',
                            'observed_property', 'feature_of_interest',
                            'procedure'),)
        '''
