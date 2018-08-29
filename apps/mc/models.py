# from django.db import models
# from django.utils.timezone import localtime
from django.contrib.gis.db import models
from django.db.models.fields import DecimalField
from django.contrib.postgres.fields import HStoreField


class TimeSeriesFeature(models.Model):
    id = models.CharField(primary_key=True, max_length=100, unique=True)

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

    content = HStoreField(blank=True, null=True, default=dict)

    class Meta:
        managed = False

    def __str__(self):
        return self.name

