# from django.db import models
from django.contrib.gis.db import models
from apps.importing.models import ProviderLog
from apps.common.models import AbstractFeature, AbstractObservation

UNIT_MUNICIPALITY = "0"
UNIT_DISTRICT = "1"
ADMIN_CHOICES = (
    (UNIT_MUNICIPALITY, 'Municipality'),
    (UNIT_DISTRICT, 'District'),
)


class AdminUnit(AbstractFeature):
    """Administrative units - municipalitites, districts"""
    id_by_provider = models.CharField(
        help_text="ID of the station used by provider.",
        max_length=50,
        editable=True
    )
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
    admin_units = models.ManyToManyField(
        AdminUnit, related_name='rsd_admin_units'
    )
    name_id = models.CharField(
        help_text="Unique and computer-friendly name of the extent",
        max_length=30,
        unique=True,
        blank=True,
        null=True,
        editable=False
    )


class CategoryCustomGroup(models.Model):
    """Custom category of an event."""
    name_id = models.CharField(
        help_text="ID of custom category",
        max_length=255,
        unique=True
    )
    name = models.CharField(
        help_text="Name of custom category",
        max_length=255,
    )


class EventCategory(models.Model):
    """Type of an event."""
    group = models.TextField(
        help_text="Event group.",
        null=True
    )
    name = models.TextField(
        help_text="Type of an event."
    )
    id_by_provider = models.CharField(
        help_text="Code of an event.",
        max_length=255,
        unique=True
    )
    custom_group = models.ForeignKey(
        CategoryCustomGroup,
        related_name='rsd_category',
        help_text="Custom category of an event.",
        on_delete=models.DO_NOTHING,
        null=True,
    )

    class Meta:
        verbose_name_plural = "Event categories"


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
        editable=True,
        on_delete=models.DO_NOTHING,
    )
    result = models.ForeignKey(
        EventExtent,
        help_text="Admin units of the event",
        related_name="rsd_result",
        editable=True,
        on_delete=models.DO_NOTHING,
    )
    point_geometry = models.PointField(
        help_text="Spatial information about event observation.",
        srid=3857,
        null=True,
    )
    provider_log = models.ForeignKey(
        ProviderLog,
        null=True,
        help_text="Reference to original provider log",
        related_name="rsd_event_observation",
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        unique_together = (('phenomenon_time_range',
                            'observed_property', 'feature_of_interest',
                            'procedure', 'id_by_provider', 'category'),)

class NumberOfEventsObservation(AbstractObservation):
    """ Represents number of events of single "category custom group" 
    that emerged in phenomenon time rage within AdminUnit. """
    feature_of_interest = models.ForeignKey(
        AdminUnit,
        help_text="Admin unit of number of event observation",
        related_name="rsd_number_of_events_observation",
        null=False,
        on_delete=models.DO_NOTHING,
    )
    category_custom_group = models.ForeignKey(
        CategoryCustomGroup,
        help_text="Custom category of number of event observation",
        related_name="rsd_number_of_events_observation",
        null=False,
        on_delete=models.DO_NOTHING,
    )
    class Meta:
        unique_together = (('phenomenon_time_range',
                            'observed_property', 'feature_of_interest',
                            'procedure','category_custom_group'),)