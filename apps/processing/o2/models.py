# coding=utf-8
import uuid
from django.db import models
from django.contrib.postgres.fields import IntegerRangeField, DateTimeRangeField
from django.utils.timezone import localtime
from psycopg2.extras import NumericRange

from apps.common.models import AbstractObservation


class Zsj(models.Model):
    """Basic residential unit in the Czech rep., officially called 'Zakladni
    sidelni jednotka'."""
    id_by_provider = models.CharField(
        help_text="ID of the ZSJ used by Czech law.",
        max_length=100,
        editable=False
    )
    name = models.CharField(
        help_text="Human-readable name of the ZSJ.",
        max_length=100
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name + ', ' + self.id_by_provider


class MobilityStream(models.Model):
    """Mobility stream from one ZSJ to another."""
    src_zsj = models.ForeignKey(
        Zsj,
        help_text="Source ZSJ, where people are departing.",
        related_name='arrival_streams',
        editable=False,
        on_delete=models.DO_NOTHING
    )
    dst_zsj = models.ForeignKey(
        Zsj,
        help_text="Destination ZSJ, where people are arriving.",
        related_name='to_streams',
        editable=False,
        on_delete=models.DO_NOTHING
    )
    opposite = models.OneToOneField(
        'self',
        help_text="Stream in opposite direction to this stream.",
        editable=False,
        null=True,
        on_delete=models.DO_NOTHING
    )

    class Meta:
        ordering = ['src_zsj__name', 'dst_zsj__name']
        unique_together = (
            (
                'src_zsj',
                'dst_zsj',
            ),
        )

    def __str__(self):
        return self.src_zsj.name + '->' + self.dst_zsj.name


ANY_OCCURRENCE = "0"
TRANSIT_OCCURRENCE = "1"
VISIT_OCCURRENCE = "2"
OCCURRENCE_CHOICES = (
    (ANY_OCCURRENCE, 'Any'),
    (TRANSIT_OCCURRENCE, 'Transit'),
    (VISIT_OCCURRENCE, 'Visit'),
)

UNIQUES_ALL = "0"
UNIQUES_UNIQUE = "1"
UNIQUES_CHOICES = (
    (UNIQUES_ALL, 'All'),
    (UNIQUES_UNIQUE, 'Uniques'),
)


class MobilityObservation(AbstractObservation):
    feature_of_interest = models.ForeignKey(
        MobilityStream,
        help_text="Stream station where the observation was taken.",
        editable=False,
        on_delete=models.DO_NOTHING
    )
    src_occurrence_type = models.CharField(
        help_text="Occurrence type in the source ZSJ.",
        max_length=1,
        choices=OCCURRENCE_CHOICES,
        default=ANY_OCCURRENCE,
    )
    dst_occurrence_type = models.CharField(
        help_text="Occurrence type in the destination ZSJ.",
        max_length=1,
        choices=OCCURRENCE_CHOICES,
        default=ANY_OCCURRENCE,
    )
    uniques_type = models.CharField(
        help_text="All or only uniques.",
        max_length=1,
        choices=UNIQUES_CHOICES,
        default=UNIQUES_ALL,
    )
    result = models.PositiveIntegerField(
        help_text="Numerical value of the measured phenomenon in units "
                  "specified by Process.",
        null=True,
        editable=False,
    )

    @property
    def result_for_human(self):
        if self.result is not None:
            res_str = "{}".format(self.result)
        else:
            reason = self.result_null_reason
            if(reason == 'HTTP Error 204'):
                reason = 'differential privacy'
            res_str = 'unknown because of ' + reason
        return res_str
    result_for_human.fget.short_description = 'Result'

    class Meta:
        get_latest_by = 'phenomenon_time_range'
        ordering = [
            '-phenomenon_time_range',
            'feature_of_interest',
            'procedure',
            'observed_property',
            'src_occurrence_type',
            'dst_occurrence_type',
            'uniques_type',
        ]
        '''
        unique_together = (
            (
                'phenomenon_time_range',
                'observed_property',
                'feature_of_interest',
                'procedure',
                'src_occurrence_type',
                'dst_occurrence_type',
                'uniques_type',
            ),
        )
        '''

    def __str__(self):
        pt_l_local = localtime(self.phenomenon_time_range.lower)
        pt_u_local = localtime(self.phenomenon_time_range.upper)

        return "{} from {} to {} on {} ({} -> {}, {}) was {}".format(
            self.observed_property.name,
            self.feature_of_interest.src_zsj.name,
            self.feature_of_interest.dst_zsj.name,
            pt_l_local.strftime('%Y-%m-%d'),
            u'{}–{}'.format(
                pt_l_local.strftime('%H:%M'),
                pt_u_local.strftime('%H:%M'),
            ),
            self.get_src_occurrence_type_display(),
            self.get_dst_occurrence_type_display(),
            self.get_uniques_type_display(),
            self.result_for_human,
        )


ANY_GENDER = "-"
MALE_GENDER = "m"
FEMALE_GENDER = "f"
GENDER_CHOICES = (
    (ANY_GENDER, 'Any'),
    (MALE_GENDER, 'Male'),
    (FEMALE_GENDER, 'Female'),
)

class SocioDemoObservation(AbstractObservation):
    feature_of_interest = models.ForeignKey(
        Zsj,
        help_text="ZSJ where the observation was taken.",
        editable=False,
        on_delete=models.DO_NOTHING
    )
    age = IntegerRangeField(
        help_text="Age of the population.",
        editable=False,
    )
    def age_for_human(self):
        if(self.age.lower==0 and self.age.upper is None):
            age = 'Any age'
        else:
            if self.age.upper is None:
                age = '{}+ years'.format(self.age.lower)
            else:
                upper = self.age.upper
                if not self.age.upper_inc:
                    upper -= 1
                age = '{}–{} years'.format(
                    self.age.lower,
                    upper
                )
        return age
    age_for_human.short_description = 'Age'
    age_for_human.admin_order_field = 'age'

    gender = models.CharField(
        help_text="Gender of the population.",
        max_length=1,
        choices=GENDER_CHOICES,
        editable=False,
        default=ANY_GENDER,
    )
    occurrence_type = models.CharField(
        help_text="Occurrence type in the ZSJ.",
        max_length=1,
        choices=OCCURRENCE_CHOICES,
        editable=False,
    )
    result = models.PositiveIntegerField(
        help_text="Numerical value of the measured phenomenon in units "
                  "specified by Process.",
        null=True,
        editable=False,
    )

    @property
    def result_for_human(self):
        if self.result is not None:
            res_str = "{}".format(self.result)
        else:
            reason = self.result_null_reason
            if(reason == 'HTTP Error 204'):
                reason = 'differential privacy'
            res_str = 'unknown because of ' + reason
        return res_str
    result_for_human.fget.short_description = 'Result'

    class Meta:
        get_latest_by = 'phenomenon_time_range'
        ordering = [
            '-phenomenon_time_range',
            'feature_of_interest',
            'observed_property',
            'procedure',
            'age',
            'gender',
            'occurrence_type',
        ]
        '''
        unique_together = (
            (
                'phenomenon_time_range',
                'observed_property',
                'feature_of_interest',
                'procedure',
                'age',
                'gender',
                'occurrence_type',
            ),
        )
        '''

    def __str__(self):
        pt_l_local = localtime(self.phenomenon_time_range.lower)
        pt_u_local = localtime(self.phenomenon_time_range.upper)

        if(self.age.lower==0 and self.age.upper is None):
            age = 'Any age'
        else:
            age = u'{}–{} years'.format(
                self.age.lower,
                getattr(self.age, 'upper', u'∞')
            )

        return "{} of {} on {} at {} ({}, {}, {}) was {}".format(
            self.observed_property.name,
            self.feature_of_interest.name,
            pt_l_local.strftime('%Y-%m-%d'),
            u'{}–{}'.format(
                pt_l_local.strftime('%H:%M'),
                pt_u_local.strftime('%H:%M'),
            ),
            age,
            self.get_gender_display() + ' gender',
            self.get_occurrence_type_display(),
            self.result_for_human,
        )
