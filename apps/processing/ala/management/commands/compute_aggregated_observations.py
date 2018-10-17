import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from importlib import import_module
from apps.common.models import Property, Process
logger = logging.getLogger(__name__)
from django.db.models import F, Func
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from apps.common.models import TimeSeries
from datetime import datetime
from apps.utils.time import UTC_P0100
from psycopg2.extras import DateTimeTZRange
from apps.common.util.util import generate_intervals
from apps.common.aggregate import aggregate
from django.db.utils import IntegrityError

from apps.processing.ala.models import SamplingFeature, Observation


#todo - move to util - pouzit jak u api, tak tady?
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


def aggregate_observations(observations, obseervation_model, prop, pt_range, feature_of_interest):
    print('AGG CALC')
    values = list(map(lambda o: o.result, observations))
    values = list(filter(lambda v: v is not None, values))
    if (len(values) == 0):
        result = None
        result_null_reason = 'only null values'
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

        obs, created = obseervation_model.objects.update_or_create(
            phenomenon_time_range=pt_range,
            observed_property=prop,
            feature_of_interest=feature_of_interest,
            procedure=process,
            defaults=defaults
        )

        obs.related_observations.set(observations)
    except IntegrityError as e:
        pass

print('NESEDI PRESNE DELKA - smazano 72 tady pocita 71')
print('NENAJDE TO POSLEDNI INTERVAL PRO VYPOCET AGG')

class Command(BaseCommand):
    help = 'recalculation'

    def handle(self, *args, **options):
        agg_providers_list = settings.APPLICATION_MC.AGGREGATED_OBSERVATIONS

        for agg_provider in agg_providers_list:
            ts_config = agg_provider.get('time_series')
            op_config = agg_provider.get('observation_providers')

            for provider in op_config:
                print('calculate provider: ', provider)

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
                    print('--')
                    print('OBSERVED_PROPERTY: ', observed_property)

                    all_features = feature_of_interest_model.objects.all()
                    for item in all_features:
                        range_from_limit = None
                        range_to_limit = None
                        max_updated_at = None
                        from_value = None
                        to_value = None

                        print('=====ITEM====')
                        print(item)

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

                        print(max_updated_at_observation)

                        if max_updated_at_observation:
                            max_updated_at = max_updated_at_observation[0].updated_at

                        if max_updated_at:
                            print('LAST AGG MAX: ', max_updated_at)
                            from_observation = provider_model.objects.filter(
                                observed_property=prop_item,
                                procedure=process,
                                feature_of_interest=item,
                                updated_at__gte=max_updated_at
                            ).annotate(
                                field_lower=Func(F('phenomenon_time_range'), function='LOWER')
                            ).order_by('field_lower')[:1]

                            print(from_observation)

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


                            print('FROM: ', from_value)
                            print('TO: ', to_value)
                            print('range_from_limit: ', range_from_limit)
                            print('range_to_limit: ', range_to_limit)
                            print('---')

                            from_value = from_value.astimezone(UTC_P0100)
                            to_value = to_value.astimezone(UTC_P0100)
                            range_from_limit = range_from_limit.astimezone(UTC_P0100)
                            range_to_limit = range_to_limit.astimezone(UTC_P0100)

                            print('FROM: ', from_value)
                            print('TO: ', to_value)
                            print('range_from_limit: ', range_from_limit)
                            print('range_to_limit: ', range_to_limit)


                            default_zero = datetime(2000, 1, 3, 0, 00, 00).replace(tzinfo=UTC_P0100)

                            t = TimeSeries(
                                zero=default_zero,
                                #frequency=relativedelta('PT1H'),
                                frequency=relativedelta(hours=1),
                                #range_from=relativedelta('PT0S'),
                                range_from=relativedelta(hours=0),
                                #range_to=relativedelta('PT1H')
                                range_to = relativedelta(hours=1)
                            )
                            t.clean()

                            result_slots = generate_intervals(
                                timeseries=t,
                                from_datetime=from_value,
                                to_datetime=to_value,
                                range_from_limit=range_from_limit,
                                range_to_limit=range_to_limit
                            )

                            print('last slot::: ', result_slots[-1])

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


        '''
        print('Posledni MERENI')
        last = Observation.objects.all().order_by('-created_at')[:1]
        print('LAST : ;:::: ', last)
        print(last[0].phenomenon_time_range)
        print(last[0].phenomenon_time_range.upper)
        print('LAST REPLACED: ', last[0].phenomenon_time_range.upper.replace(tzinfo=UTC_P0100))
        print('LAST AS: ', last[0].phenomenon_time_range.upper.astimezone(UTC_P0100))
        '''