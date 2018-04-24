from apps.common.models import AbstractFeature, AbstractObservation
from django.contrib.gis.db import models


class MeteoStation(AbstractFeature):
    # Ala doesn't have geometry value to the yet - to be added in future

    geometry = models.PointField(
        help_text="Spatial information about station.",
        srid=3857
    )

    watercourse = models.CharField(
        help_text="Human-readable name of the watercourse.",
        max_length=150
    )

