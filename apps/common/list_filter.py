# implement it for phenomenon time
# https://docs.djangoproject.com/en/2.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter

from django.contrib import admin
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, date, timedelta
from dateutil.parser import parse
from psycopg2.extras import DateTimeTZRange
from apps.utils.time import UTC_P0100
from psycopg2.extras import NumericRange


class DateRangeDurationFilter(admin.SimpleListFilter):
    title = 'phenomenon duration'
    parameter_name = 'phenomenon_time_range__duration'

    def lookups(self, request, model_admin):
        lt = str(0) + '--' + str(3600)
        gt = str(3600) + '--' + str(99999)

        return (
            (0, 'instant'),
            (600, '10 minutes'),
            (900, '15 minutes'),
            (3600, 'hour'),
            (lt, 'Less than hour'),
            (gt, 'Hour and longer')
        )

    def queryset(self, request, queryset):
        v = self.value()
        if v == None:
            return queryset

        if isinstance(v, str):
            values = v.split('--')
            if len(values) == 2:
                v = NumericRange(int(values[0]), int(values[1]))
            else:
                v = self.value()

        return queryset.filter(
            phenomenon_time_range__duration=v
        )


class DateRangeRangeFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'phenomenon time'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'phenomenon_time'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        today = date.today()
        this_monday = today - timedelta(days=today.weekday())
        next_monday = this_monday + timedelta(weeks=1)
        prev_monday = this_monday - timedelta(weeks=1)
        this_monday = this_monday.strftime('%Y-%m-%d')
        next_monday = next_monday.strftime('%Y-%m-%d')
        prev_monday = prev_monday.strftime('%Y-%m-%d')
        this_week = this_monday + '--' + next_monday
        last_week = prev_monday + '--' + this_monday
        return (
            (this_week, 'this week'),
            (last_week, 'last week'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        v = self.value()
        if v == None:
            return queryset
        dt_from, dt_to = list(map(
            lambda p: datetime.combine(
                parse(p),
                datetime.min.time()
            ).replace(tzinfo=UTC_P0100),
            v.split('--')
        ))
        dt_range = DateTimeTZRange(dt_from, dt_to)

        return queryset.filter(
            phenomenon_time_range__contained_by=dt_range
        )


class ResultNullReasonFilter(admin.AllValuesFieldListFilter):
    def choices(self, changelist):
        yield {
            'selected': self.lookup_val is None and self.lookup_val_isnull is None,
            'query_string': changelist.get_query_string({}, [self.lookup_kwarg, self.lookup_kwarg_isnull]),
            'display': _('All'),
        }
        yield {
            'selected': self.lookup_val == "" and self.lookup_val_isnull is None,
            'query_string': changelist.get_query_string(
                {
                    self.lookup_kwarg: ""
                },
                [self.lookup_kwarg_isnull]
            ),
            'display': _('Empty (result exists)'),
        }
        include_none = False
        for val in self.lookup_choices:
            if val is None:
                include_none = True
                continue
            if val == "":
                continue
            val = force_text(val)
            yield {
                'selected': self.lookup_val == val,
                'query_string': changelist.get_query_string({
                    self.lookup_kwarg: val,
                }, [self.lookup_kwarg_isnull]),
                'display': val,
            }
        if include_none:
            yield {
                'selected': bool(self.lookup_val_isnull),
                'query_string': changelist.get_query_string({
                    self.lookup_kwarg_isnull: 'True',
                }, [self.lookup_kwarg]),
                'display': self.empty_value_display,
            }
