from __future__ import absolute_import, unicode_literals
from importlib import import_module

from django.conf import settings
from django.db.models import F, Func
from django.db.utils import IntegrityError
from django.utils.dateparse import parse_datetime

from celery.task import task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

from apps.common.models import Property, Process
from apps.common.models import TimeSeries
from apps.common.util.util import generate_intervals
from apps.common.aggregate import aggregate
from apps.utils.time import UTC_P0100
from django.utils import timezone


def import_models(path):
    provider_module = None
    provider_model = None
    error_message = None
    try:
        path = path.rsplit('.', 1)
        provider_module = import_module(path[0])
        provider_model = getattr(provider_module, path[1])
        return provider_model, provider_module, error_message
    except ModuleNotFoundError as e:
        error_message = 'module not found'
        return provider_model, provider_module, error_message
    except AttributeError as e:
        error_message = 'function not found'
        return provider_model, provider_module, error_message


def aggregate_observations(observations, observation_model, prop, pt_range, feature_of_interest):
    values = list(map(lambda o: o.result, observations))
    values = list(filter(lambda v: v is not None, values))
    if (len(values) == 0):
        return None
    else:
        result, result_null_reason, process = aggregate(prop, values)

    if result is None:
        logger.warning(
            "Result_null_reason of hourly average, "
            "station {}, property {}, pt_range {}: {}".format(
                feature_of_interest.id_by_provider,
                prop.name_id,
                pt_range,
                result_null_reason
            )
        )

    try:
        defaults = {
            'phenomenon_time_range': pt_range,
            'observed_property': prop,
            'feature_of_interest': feature_of_interest,
            'procedure': process,
            'result': result,
            'result_null_reason': result_null_reason
        }

        obs, created = observation_model.objects.update_or_create(
            phenomenon_time_range=pt_range,
            observed_property=prop,
            feature_of_interest=feature_of_interest,
            procedure=process,
            defaults=defaults
        )

        obs.related_observations.set(observations)
    except IntegrityError as e:
        pass


@task(name="mc.compute_aggregated_values")
def compute_aggregated_values(aggregate_updated_since_datetime=None):
    aggregate_updated_since = None
    if aggregate_updated_since_datetime:
        aggregate_updated_since = aggregate_updated_since_datetime
        aggregate_updated_since = parse_datetime(aggregate_updated_since)

    if aggregate_updated_since_datetime and aggregate_updated_since is None:
        raise Exception('Aggregate_updated_since is not valid datetime')

    if aggregate_updated_since and aggregate_updated_since.tzinfo is None:
        aggregate_updated_since = aggregate_updated_since.replace(tzinfo=UTC_P0100)

    agg_providers_list = settings.APPLICATION_MC.AGGREGATED_OBSERVATIONS

    for agg_provider in agg_providers_list:
        ts_config = agg_provider.get('time_series')

        zero = parse_datetime(ts_config['zero'])
        frequency = ts_config['frequency']
        range_from = ts_config['range_from']
        range_to = ts_config['range_to']

        t = TimeSeries(
            zero=zero,
            frequency=frequency,
            range_from=range_from,
            range_to=range_to
        )

        t.full_clean()
        t.clean()

        op_config = agg_provider.get('observation_providers')

        for provider in op_config:

            provider_module, provider_model, error_message = import_models(provider)
            if error_message:
                raise Exception("Importing error - %s : %s" % (provider, error_message))

            feature_of_interest_model = provider_module._meta.get_field(
                'feature_of_interest').remote_field.model

            path = provider.rsplit('.', 1)
            provider_module = import_module(path[0])
            provider_model = getattr(provider_module, path[1])

            try:
                process = Process.objects.get(
                    name_id=op_config[provider]["process"])
            except Process.DoesNotExist:
                process = None

            observed_properties = op_config[provider]["observed_properties"]
            for observed_property in observed_properties:
                prop_item = Property.objects.get(name_id=observed_property)

                all_features = feature_of_interest_model.objects.all()
                for item in all_features:
                    range_from_limit = None
                    range_to_limit = None
                    max_updated_at = None
                    from_value = None
                    to_value = None

                    range_to_limit_observation = provider_model.objects.filter(
                        observed_property=prop_item,
                        procedure=process,
                        feature_of_interest=item
                    ).annotate(
                        field_upper=Func(F('phenomenon_time_range'), function='UPPER')
                    ).order_by('-field_upper')[:1]

                    if not range_to_limit_observation:
                        break
                    range_to_limit = range_to_limit_observation[0].phenomenon_time_range.upper

                    range_from_limit_observation = provider_model.objects.filter(
                        observed_property=prop_item,
                        procedure=process,
                        feature_of_interest=item
                    ).annotate(
                        field_lower=Func(F('phenomenon_time_range'), function='LOWER')
                    ).order_by('field_lower')[:1]
                    if not range_from_limit_observation:
                        break

                    range_from_limit = range_from_limit_observation[0].phenomenon_time_range.lower

                    max_updated_at_observation = provider_model.objects.filter(
                        observed_property=prop_item,
                        procedure=prop_item.default_mean,
                        feature_of_interest=item
                    ).order_by('-updated_at')[:1]

                    if max_updated_at_observation and not aggregate_updated_since:
                        max_updated_at = max_updated_at_observation[0].updated_at
                    elif aggregate_updated_since:
                        max_updated_at = aggregate_updated_since

                    if max_updated_at:
                        from_observation = provider_model.objects.filter(
                            observed_property=prop_item,
                            procedure=process,
                            feature_of_interest=item,
                            updated_at__gte=max_updated_at
                        ).annotate(
                            field_lower=Func(F('phenomenon_time_range'), function='LOWER')
                        ).order_by('field_lower')[:1]

                        if from_observation:
                            from_value = from_observation[0].phenomenon_time_range.lower

                        to_observation = provider_model.objects.filter(
                            observed_property=prop_item,
                            procedure=process,
                            feature_of_interest=item,
                            updated_at__gte=max_updated_at
                        ).annotate(
                            field_upper=Func(F('phenomenon_time_range'), function='UPPER')
                        ).order_by('-field_upper')[:1]

                        if to_observation:
                            to_value = to_observation[0].phenomenon_time_range.upper

                    else:
                        from_value = range_from_limit
                        to_value = range_to_limit

                    if from_value and to_value:
                        from_value = from_value.astimezone(UTC_P0100)
                        to_value = to_value.astimezone(UTC_P0100)
                        # range_from_limit = range_from_limit.astimezone(UTC_P0100)
                        # range_to_limit = range_to_limit.astimezone(UTC_P0100)

                        result_slots = generate_intervals(
                            timeseries=t,
                            from_datetime=from_value,
                            to_datetime=to_value  # ,
                            # range_from_limit=range_from_limit,
                            # range_to_limit=range_to_limit
                        )

                        for slot in result_slots:
                            observations = provider_model.objects.filter(
                                observed_property=prop_item,
                                procedure=process,
                                feature_of_interest=item,
                                phenomenon_time_range__contained_by=slot
                            )

                            ids_to_agg = []
                            for obs in observations:
                                ids_to_agg.append(obs.id)

                            aggregate_observations(observations, provider_model, prop_item, slot, item)

