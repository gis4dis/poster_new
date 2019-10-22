from django.contrib.gis.db import models
from apps.common.models import AbstractFeature, AbstractObservation


class SamplingFeature(AbstractFeature):
    geometry = models.PointField(
        help_text="Spatial information about feature.",
        srid=3857
    )


class Observation(AbstractObservation):
    feature_of_interest = models.ForeignKey(
        SamplingFeature,
        help_text="Watercourse station where the observation was taken.",
        related_name='observations',
        editable=False,
        on_delete=models.DO_NOTHING
    )

    class Meta:
        get_latest_by = 'phenomenon_time_range'
        ordering = ['-phenomenon_time_range', 'feature_of_interest', 'procedure',
                    'observed_property']
        # unique_together see migration 0005 and 0006, index ozp_observation_uniq

