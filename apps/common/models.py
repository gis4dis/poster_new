# from django.db import models
# from django.utils.timezone import localtime
from django.contrib.gis.db import models
from django.contrib.postgres import fields as pgmodels
from apps.utils.time import format_delta


class Process(models.Model):
    """Process used to generate the result, e.g. measurement or
    hourly average."""
    name_id = models.CharField(
        help_text="Unique and computer-friendly name of the process. eg. ('measure' or 'avg_hour')",
        max_length=100,
        unique=True,
        editable=False
    )
    name = models.CharField(
        help_text="Human-readable name of the process.",
        max_length=50
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = "processes"

    def __str__(self):
        return self.name


class Property(models.Model):
    """Physical phenomenon related to weather, e.g. air temperature."""

    name_id = models.CharField(
        help_text="Unique and computer-friendly name of the property. eg. ('precipitation' or 'air_temperature')",
        max_length=30,
        unique=True,
        editable=False
    )

    name = models.CharField(
        help_text="Human-readable name of the property.",
        max_length=30
    )

    unit = models.CharField(
        help_text="Unit of observations (physical unit). Same for all "
                  "observations of the property.",
        max_length=30
    )

    default_mean = models.ForeignKey(
        Process,
        null=True,
        help_text="Process aggregation used to calculate the result.",
        related_name="%(app_label)s_%(class)s_related",
        editable=False,
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = "properties"

    def __str__(self):
        return self.name


class AbstractFeature(models.Model):
    """Place where the observation were collected - mostly point feature like weather station."""

    id_by_provider = models.CharField(
        help_text="ID of the station used by provider.",
        max_length=50,
        editable=False
    )

    name = models.CharField(
        help_text="Human-readable name of the station.",
        max_length=50
    )

    # https://docs.djangoproject.com/en/1.10/topics/db/models/#field-name-hiding-is-not-permitted
    # This field is supposed to be overridden in subclass if needed.
    # By default it is set to point geometry (PointField) but could be either changed on other type (LineField)
    #   or completely removed (set to None)
    # https://docs.djangoproject.com/en/1.11/ref/contrib/gis/model-api/#pointfield
    #
    # Spatial fields defaults to srid=4326 (WGS84)
    geometry = models.PointField(
        help_text="Spatial information about feature."
    )

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


class AbstractObservation(models.Model):
    """An observation is an act associated with a discrete time instant or
    period through which a quantity is assigned to a phenomenon (Property).
    It involves application of a specified procedure (Process), such as a
    sensor measurement or algorithm processing (e.g. hourly average)."""

    phenomenon_time_range = pgmodels.DateTimeRangeField(
        help_text="Datetime range when the observation was captured.",
    )

    def phenomenon_time_from(self):
        return self.phenomenon_time_range.lower
    phenomenon_time_from.admin_order_field = 'phenomenon_time_range'

    @property
    def phenomenon_time_duration(self):
        delta = self.phenomenon_time_range.upper - self.phenomenon_time_range.lower
        return delta

    @property
    def phenomenon_time_duration_for_human(self):
        return format_delta(self.phenomenon_time_duration)
    phenomenon_time_duration_for_human.fget.short_description = "Phenomenon time duration"

    # phenomenon_time_to = models.DateTimeField(
    #     help_text="End of the observation. If the observation was instant, "
    #               "it is the same time as phenomenon_time.",
    #     editable=False
    # )

    observed_property = models.ForeignKey(
        Property,
        help_text="Phenomenon that was observed, e.g. air temperature.",
        related_name="%(app_label)s_%(class)s_related",
        editable=False,
        on_delete=models.DO_NOTHING,
    )

    # NOTE: This field has to be overridden in child classes!
    #       It needs to reference proper ForeignKey (Concrete Feature inherited from AbstractFeature)
    feature_of_interest = models.ForeignKey(
        AbstractFeature,
        help_text="Weather station where the observation was taken.",
        related_name="%(app_label)s_%(class)s_related",
        editable=False,
        on_delete=models.DO_NOTHING,
    )

    procedure = models.ForeignKey(
        Process,
        help_text="Process used to generate the result, e.g. measurement or "
                  "average.",
        related_name="%(app_label)s_%(class)s_related",
        editable=False,
        on_delete=models.DO_NOTHING,
    )

    related_observations = models.ManyToManyField(
        'self',
        help_text="Measured observations that were used to generate average "
                  "observation, or vice versa.",
        editable=False,
    )

    result = models.DecimalField(
        help_text="Numerical value of the measured phenomenon in units "
                  "specified by Process.",
        max_digits=8,
        decimal_places=3,
        null=True,
        editable=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    @property
    def result_for_human(self):
        if self.result is not None:
            res_str = "{}".format(self.result)
        else:
            reason = self.result_null_reason
            res_str = 'unknown because of ' + reason
        return res_str
    result_for_human.fget.short_description = 'Result'

    result_null_reason = models.CharField(
        help_text="Reason why result is null.",
        max_length=100,
        default='',
    )

    class Meta:
        abstract = True
        get_latest_by = 'phenomenon_time_range'
        ordering = ['-phenomenon_time_range', 'feature_of_interest', 'procedure',
                    'observed_property']
        unique_together = (('phenomenon_time_range',
                            'observed_property', 'feature_of_interest',
                            'procedure'),)

