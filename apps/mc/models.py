# from django.db import models
# from django.utils.timezone import localtime
from django.contrib.gis.db import models
from django.db.models.fields import DecimalField
from django.contrib.postgres.fields import ArrayField


class TimeSeriesFeature(models.Model):
    id_by_provider = models.CharField(
        help_text="ID of the station used by provider.",
        max_length=50,
        editable=False
    )

    name = models.CharField(
        help_text="Human-readable name of the station.",
        max_length=50
    )

    geometry = models.PointField(
        help_text="Spatial information about feature."
    )

    property_values = ArrayField(DecimalField(decimal_places=5, max_digits=15), null=True, blank=True)
    property_anomaly_rates = ArrayField(DecimalField(decimal_places=5, max_digits=15), null=True, blank=True)
    phenomenon_time_from = models.DateTimeField()
    phenomenon_time_to = models.DateTimeField()
    value_index_shift = models.IntegerField()

    class Meta:
        managed = False

    def __str__(self):
        return self.name

