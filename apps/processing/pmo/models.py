from apps.common.models import AbstractFeature, AbstractObservation
from django.contrib.gis.db import models


class WatercourseStation(AbstractFeature):
    # Ala doesn't have geometry value to the yet - to be added in future

    geometry = models.PointField(
        help_text="Spatial information about station.",
        srid=3857
    )

    watercourse = models.CharField(
        help_text="Human-readable name of the watercourse.",
        max_length=150
    )



class WatercourseObservation(AbstractObservation):
    # NOTE: see parent class for more information
    feature_of_interest = models.ForeignKey(
        WatercourseStation,
        help_text="Watercourse station where the observation was taken.",
        related_name='watercourse_observations',
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
                            

class WeatherStation(AbstractFeature):
    geometry = models.PointField(
        help_text="Spatial information about station.",
        srid=3857,
        null=True
    )

    basin = models.CharField(
        help_text="Human-readable name of the basin.",
        max_length=150,
        null = True
    )


class WeatherObservation(AbstractObservation):
    feature_of_interest = models.ForeignKey(
        WeatherStation,
        help_text="Weather station where the observation was taken.",
        related_name="%(app_label)s_%(class)s_related",
        editable=False,
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        unique_together = ()
