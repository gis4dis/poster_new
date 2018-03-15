# from django.db import models
from django.contrib.gis.db import models

from apps.common.models import AbstractFeature, AbstractObservation

UNIT_MUNICIPALITY = "0"
UNIT_DISTRICT = "1"
ADMIN_CHOICES = (
    (UNIT_MUNICIPALITY, 'Municipality'),
    (UNIT_DISTRICT, 'District'),
)

class AdminUnit(AbstractFeature):
    """Administrative units - municipalitites, districts"""
    geometry = models.MultiPolygonField(
        help_text="Spatial information about feature.",
        srid=3857
    )
    level = models.CharField(
        help_text="Municipality or district.",
        max_length=255,
        choices=ADMIN_CHOICES,
        default=UNIT_MUNICIPALITY,
    )


class EventExtent(models.Model):
    """Extent of an event - multiple AdminUnits."""
    admin_units = models.ManyToManyField(AdminUnit, related_name='rsd_admin_units')


class EventCategory(models.Model):
    """Type of an event."""
    name = models.CharField(
        help_text="Type of an event.",
        max_length=255,
        unique=True
    )
    id_by_provider = models.CharField(
        help_text="Code of an event.",
        max_length=255,
        unique=True
    )
    
class EventObservation(AbstractObservation):
    """The observed event"""
    feature_of_interest = models.ForeignKey(
        EventExtent,
        related_name='rsd_feature_of_interest',
        help_text="Admin units of Brno+Brno-venkov+D1",
        editable=False,
        on_delete=models.DO_NOTHING,
    )
    id_by_provider = models.TextField(
        help_text="Unique ID of an event.",
    )
    category = models.ForeignKey(
        EventCategory,
        related_name='rsd_category',
        help_text="Type of an event.",
        editable=False,
        on_delete=models.DO_NOTHING,
    )
    result = models.ForeignKey(
        EventExtent,
        help_text="Admin units of the event",
        related_name="rsd_result",
        editable=False,
        on_delete=models.DO_NOTHING,
    )
    class Meta:
        unique_together = (('phenomenon_time_range',
                            'observed_property', 'feature_of_interest',
                            'procedure','id_by_provider','category'),)

