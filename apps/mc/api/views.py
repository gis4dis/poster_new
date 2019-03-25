from importlib import import_module

import requests
from contextlib import closing

from dateutil import relativedelta
from dateutil.parser import parse
from django.conf import settings
from django.contrib.gis.geos import Polygon
from psycopg2.extras import DateTimeTZRange
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime

from apps.ad.anomaly_detection import get_timeseries
from apps.common.models import Property, Process
from apps.common.models import Topic
from apps.mc.models import TimeSeriesFeature
from apps.common.models import TimeSlots
from apps.mc.api.serializers import PropertySerializer, TimeSeriesSerializer, TopicSerializer
from apps.utils.time import UTC_P0100
from apps.common.util.util import generate_intervals
from django.db.models import Max, Min
from django.db.models import F, Func, Q
from apps.common.util.util import get_time_slots_by_id

from datetime import timedelta

from functools import partial

from datetime import timedelta

from functools import partial


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


def parse_date_range(from_string, to_string):
    if from_string:
        try:
            day_from = parse(from_string)
        except ValueError as e:
            raise APIException("Phenomenon_date_from is not valid")

    if to_string:
        try:
            day_to = parse(to_string)
            day_to = day_to + relativedelta.relativedelta(days=1)
        except ValueError as e:
            raise APIException("Phenomenon_date_to is not valid")

    if day_from > day_to:
        raise APIException("Phenomenon_date_from bound must be less than or equal phenomenon_date_to")

    time_range_boundary = '[]' if day_from == day_to else '[)'

    pt_range = DateTimeTZRange(
        day_from, day_to, time_range_boundary)

    return pt_range, day_from, day_to


def float_bbox_param(value):
    try:
        float_val = float(value)
        return float_val
    except:
        raise APIException("BBOX param float conversion error: %s" % value)


def validate_bbox_values(bbox_array):
    if bbox_array[0] >= bbox_array[2]:
        raise APIException("BBOX minx is not < maxx")

    if bbox_array[1] >= bbox_array[3]:
        raise APIException("BBOX miny is not < maxy")


def parse_properties(properties_string):
    properties_parts = properties_string.rsplit(',')
    return properties_parts


def parse_bbox(bbox_string):
    bbox_parts = bbox_string.rsplit(',')

    if len(bbox_parts) != 4:
        raise APIException("BBOX 4 parameters required")

    x_min = float_bbox_param(bbox_parts[0])
    y_min = float_bbox_param(bbox_parts[1])
    x_max = float_bbox_param(bbox_parts[2])
    y_max = float_bbox_param(bbox_parts[3])

    if x_min and y_min and x_max and y_max:
        bbox = (x_min, y_min, x_max, y_max)
        validate_bbox_values(bbox)
        geom_bbox = Polygon.from_bbox(bbox)
    else:
        raise APIException("Error in passed query parameter: bbox")

    return geom_bbox


class PropertyViewSet(viewsets.ViewSet):
    def list(self, request):
        if 'topic' in request.GET:
            topic_param = request.GET['topic']
            topic = settings.APPLICATION_MC.TOPICS.get(topic_param)

            if not topic or not Topic.objects.filter(name_id=topic_param).exists():
                raise APIException('Topic not found.')

            prop_names = list(topic['properties'].keys())

            queryset = Property.objects.filter(name_id__in=prop_names)
            serializer = PropertySerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            raise APIException("Parameter topic is required")


class VgiViewSet(viewsets.ReadOnlyModelViewSet):
    def list(self, request, format=None):
        if 'topic' in request.GET:
            topic_param = request.GET['topic']
            topic = settings.APPLICATION_MC.TOPICS.get(topic_param)

            if not topic or not Topic.objects.filter(name_id=topic_param).exists():
                raise APIException('Topic not found.')
        else:
            raise APIException("Parameter topic is required")

        if 'phenomenon_date_from' in request.GET:
            phenomenon_date_from = request.GET['phenomenon_date_from']
        else:
            raise APIException("Parameter phenomenon_date_from is required")

        if 'phenomenon_date_to' in request.GET:
            phenomenon_date_to = request.GET['phenomenon_date_to']
        else:
            raise APIException("Parameter phenomenon_date_to is required")

        pt_range, day_from, day_to = parse_date_range(phenomenon_date_from, phenomenon_date_to)

        payload = {
            'from': day_from.strftime('%Y-%m-%d'),
            'to': day_to.strftime('%Y-%m-%d'),
            'category': topic_param
        }

        with closing(requests.get('https://zelda.sci.muni.cz/rest/api/observations', params=payload, verify=False)) as r:
            if r.status_code != 200:
                return Response({"type": "FeatureCollection", "features": []})
            res = r.json()
            return Response(res)

        return Response({"type": "FeatureCollection", "features": []})



class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    topics = settings.APPLICATION_MC.TOPICS.keys()
    queryset = Topic.objects.filter(name_id__in=list(topics))
    serializer_class = TopicSerializer


# http://localhost:8000/api/v2/timeseries/?topic=drought&properties=air_temperature,ground_air_temperature&phenomenon_date_from=2018-01-20&phenomenon_date_to=2018-09-27&bbox=1826997.8501,6306589.8927,1846565.7293,6521189.3651
# http://localhost:8000/api/v2/timeseries?topic=drought&properties=air_temperature,ground_air_temperature&phenomenon_date_from=2018-01-20&phenomenon_date_to=2018-09-27

def get_index_shift(time_slots, first_item_from, current_item_from):
    first_idx = None
    current_idx = None
    for idx in range(len(time_slots)):
        slot = time_slots[idx]
        if slot.lower == first_item_from:
            first_idx = idx
        if slot.lower == current_item_from:
            current_idx = idx

        if first_idx and current_idx:
            break

    return current_idx - first_idx


def get_value_frequency(t, from_datetime):
    to = from_datetime + t.frequency + t.frequency
    result_slots = generate_intervals(
        timeslots=t,
        from_datetime=from_datetime,
        to_datetime=to,
    )

    if len(result_slots) < 2:
        return None

    diff = (result_slots[1].lower - result_slots[0].lower).total_seconds()
    return diff


def get_empty_slots(t, pt_range_z):
    return generate_intervals(
        timeslots=t,
        from_datetime=pt_range_z.lower,
        to_datetime=pt_range_z.upper,
    )


def get_observations(
    time_slots,
    observed_property,
    observation_provider_model,
    feature_of_interest,
    process,
    t,
    lag_window_size,
    future_window_size
):

    before_intervals = []
    after_intervals = []
    time_slot_diff = time_slots[1].lower - time_slots[0].lower

    if lag_window_size and lag_window_size > 0:
        bef_time_diff = time_slot_diff * lag_window_size + \
                      (time_slots[0].upper - time_slots[0].lower)
        bef_time_diff = bef_time_diff.total_seconds()

        from_datetime = time_slots[0].lower - timedelta(seconds=bef_time_diff)

        before_intervals = generate_intervals(
            timeslots=t,
            from_datetime=from_datetime,
            to_datetime=time_slots[0].lower,
        )

        before_intervals = before_intervals[-lag_window_size:]

    if future_window_size and future_window_size > 0:
        after_time_diff = time_slot_diff * future_window_size + \
                        (time_slots[0].upper - time_slots[0].lower)
        after_time_diff = after_time_diff.total_seconds()

        to_datetime = time_slots[-1].lower + timedelta(seconds=after_time_diff)

        after_intervals = generate_intervals(
            timeslots=t,
            from_datetime=time_slots[-1].lower,
            to_datetime=to_datetime,
        )

        after_intervals = after_intervals[1:]
        after_intervals = after_intervals[-future_window_size:]

    extended_time_slots =  before_intervals + time_slots + after_intervals

    return prepare_data(
        extended_time_slots,
        observed_property,
        observation_provider_model,
        feature_of_interest,
        process
    )


def prepare_data(
    time_slots,
    observed_property,
    observation_provider_model,
    feature_of_interest,
    process
):
    obss = observation_provider_model.objects.filter(
        observed_property=observed_property,
        procedure=process,
        feature_of_interest=feature_of_interest,
        phenomenon_time_range__in=time_slots
    )

    obs_reduced = {obs.phenomenon_time_range.lower.timestamp(): obs for obs in obss}
    observations = []

    for i in range(0, len(time_slots)):
        slot = time_slots[i]
        st = slot.lower.timestamp()
        obs = None

        if st in obs_reduced and obs_reduced[st] and obs_reduced[st].result is not None:
            obs = obs_reduced[st]

        if obs is None:
            obs = observation_provider_model(
                phenomenon_time_range=slot,
                observed_property=observed_property,
                feature_of_interest=feature_of_interest,
                procedure=process,
                result=None
            )
        observations.append(obs)
    return observations


def get_not_null_ranges(
    features,
    props,
    topic_config,
    observation_provider_name,
    provider_model,
    pt_range_z
):
    q_objects = Q()

    prop_items = {}
    process_items = {}

    for item in features:
        for prop in props:
            prop_config = topic_config['properties'][prop]
            process_name_id = prop_config['observation_providers'][observation_provider_name]["process"]

            try:
                process = process_items[process_name_id]
            except KeyError:
                try:
                    process = Process.objects.get(name_id=process_name_id)
                    process_items[process_name_id] = process
                except Process.DoesNotExist:
                    process = None

            if not process:
                raise APIException('Process from config not found.')

            try:
                prop_item = prop_items[prop]
            except KeyError:
                prop_item = Property.objects.get(name_id=prop)
                prop_items[prop] = prop_item

            q_objects.add(Q(
                observed_property=prop_item,
                feature_of_interest=item,
                procedure=process
            ), Q.OR)

    q_objects.add(Q(
        phenomenon_time_range__overlap=pt_range_z
    ), Q.AND)

    pm = provider_model.objects.filter(
        q_objects
    ).values(
        'feature_of_interest',
        'procedure',
        'observed_property',
    ).annotate(
        min_b=Min(Func(F('phenomenon_time_range'), function='LOWER')),
        max_b=Max(Func(F('phenomenon_time_range'), function='UPPER'))
    ).order_by('feature_of_interest')

    return pm


def get_feature_nn_from_list(
    nn_list,
    feature,
    prop_id,
    process_id
):
    for item in nn_list:
        if item['feature_of_interest'] == feature.id and item['procedure'] == process_id and item['observed_property'] == prop_id:
            return DateTimeTZRange(
                item['min_b'],
                item['max_b']
            )

    return None


def get_not_null_range(
    pt_range,
    observed_property,
    observation_provider_model,
    feature_of_interest,
    process
):

    obs_first = observation_provider_model.objects.filter(
        observed_property=observed_property,
        procedure=process,
        feature_of_interest=feature_of_interest,
        phenomenon_time_range__overlap=pt_range
    ).order_by('phenomenon_time_range')[:1]

    obs_latest = observation_provider_model.objects.filter(
        observed_property=observed_property,
        procedure=process,
        feature_of_interest=feature_of_interest,
        phenomenon_time_range__overlap=pt_range
    ).order_by('-phenomenon_time_range')[:1]

    if obs_first:
        return  DateTimeTZRange(
            obs_first[0].phenomenon_time_range.lower,
            obs_latest[0].phenomenon_time_range.upper
        )

    return None


def get_first_observation_duration(
    pt_range,
    observed_property,
    observation_provider_model,
    feature_of_interest,
    process
):
    observations = observation_provider_model.objects.filter(
        observed_property=observed_property,
        procedure=process,
        feature_of_interest=feature_of_interest,
        phenomenon_time_range__overlap=pt_range
    ).order_by('phenomenon_time_range')[:1]

    if len(observations) > 0:
        value_duration = observations[0].phenomenon_time_range.upper \
                         - observations[0].phenomenon_time_range.lower
        value_duration = value_duration.total_seconds()
        return value_duration

    return None


USE_DYNAMIC_TIMESLOTS = True
ROUND_DECIMAL_SPACES = 3

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


#http://localhost:8000/api/v2/timeseries/?topic=drought&properties=air_temperature&phenomenon_date_from=2018-10-29&phenomenon_date_to=2018-10-30
class TimeSeriesViewSet(viewsets.ViewSet):

    #@method_decorator(cache_page(60*60*12))
    def list(self, request):
        if 'topic' in request.GET:
            topic = request.GET['topic']
        else:
            raise APIException('Parameter topic is required')

        topic_config = settings.APPLICATION_MC.TOPICS.get(topic)

        if not topic_config or not Topic.objects.filter(name_id=topic).exists():
            raise APIException('Topic not found.')

        properties = topic_config['properties']

        if 'properties' in request.GET:
            properties_string = request.GET['properties']
            param_properties = parse_properties(properties_string)

            for prop in param_properties:
                if not properties.get(prop):
                    raise APIException('Property: ' + prop + ' does not exist in config')

                try:
                    Property.objects.get(name_id=prop)
                except Property.DoesNotExist:
                    raise APIException('Property from config not found.')

        else:
            param_properties = properties.keys()
            db_filtered_props = []
            for prop in param_properties:
                try:
                    Property.objects.get(name_id=prop)
                    db_filtered_props.append(prop)
                except Property.DoesNotExist:
                    raise APIException('Config has property not present in datbaase.')

        if 'phenomenon_date_from' in request.GET:
            phenomenon_date_from = request.GET['phenomenon_date_from']
        else:
            raise APIException("Parameter phenomenon_date_from is required")

        if 'phenomenon_date_to' in request.GET:
            phenomenon_date_to = request.GET['phenomenon_date_to']
        else:
            raise APIException("Parameter phenomenon_date_to is required")

        pt_range, day_from, day_to = parse_date_range(phenomenon_date_from, phenomenon_date_to)

        pt_range_z = DateTimeTZRange(
            pt_range.lower.replace(tzinfo=UTC_P0100),
            pt_range.upper.replace(tzinfo=UTC_P0100)
        )

        try:
            time_slots_config = topic_config['time_slots']
        except KeyError:
            raise APIException('Topic has no time_slots configuration.')

        if not time_slots_config or len(time_slots_config) < 1:
            raise APIException('Topic time_slots configuration is empty.')

        ts_id = topic_config['time_slots'][0]
        if 'time_slots' in request.GET:
            ts_param = request.GET['time_slots']
            if ts_param not in topic_config['time_slots']:
                raise APIException('Requested time_slots is not available.')
            else:
                ts_id = ts_param

        ts_config = get_time_slots_by_id(ts_id)
        if not ts_config:
            raise APIException('Default time_slots config not found.')

        zero = parse_datetime(ts_config['zero'])
        frequency = ts_config['frequency']
        range_from = ts_config['range_from']
        range_to = ts_config['range_to']
        name = ts_config['name']

        t = TimeSlots(
            zero=zero,
            frequency=frequency,
            range_from=range_from,
            range_to=range_to,
            name=name
        )

        t.full_clean()
        t.clean()

        if USE_DYNAMIC_TIMESLOTS is True:
            time_slots = None #[]
        else:
            time_slots = get_empty_slots(t, pt_range_z)

        value_frequency = get_value_frequency(t, zero)
        value_duration = None

        geom_bbox = None
        if 'bbox' in request.GET:
            bbox = request.GET['bbox']
            geom_bbox = parse_bbox(bbox)

        model_props = {}

        if topic_config:
            for prop in param_properties:
                prop_config = properties.get(prop)
                op = prop_config['observation_providers']

                for provider in op:
                    if provider in model_props:
                        model_props[provider].append(prop)
                    else:
                        model_props[provider] = [prop]

        time_series_list = []
        phenomenon_time_from = None
        phenomenon_time_to = None
        process_items = {}
        prop_items = {}

        for model in model_props:

            provider_module, provider_model, error_message = import_models(model)
            if error_message:
                raise APIException("Importing error - %s : %s" % (model, error_message))

            path = model.rsplit('.', 1)
            provider_module = import_module(path[0])
            provider_model = getattr(provider_module, path[1])

            feature_of_interest_model = provider_model._meta.get_field('feature_of_interest').remote_field.model

            if geom_bbox:
                all_features = feature_of_interest_model.objects.filter(geometry__intersects=geom_bbox)
            else:
                all_features = feature_of_interest_model.objects.all()

            observation_provider_model_name = f"{provider_model.__module__}.{provider_model.__name__}"

            nn_feature_ranges = get_not_null_ranges(
                features=all_features,
                props=model_props[model],
                topic_config=topic_config,
                observation_provider_name=observation_provider_model_name,
                provider_model=provider_model,
                pt_range_z=pt_range_z
            )

            for item in all_features:
                content = {}

                has_values = False
                f_phenomenon_time_from = None
                f_phenomenon_time_to = None

                for prop in model_props[model]:
                    prop_config = topic_config['properties'][prop]

                    process_name_id = prop_config['observation_providers'][observation_provider_model_name]["process"]
                    try:
                        process = process_items[process_name_id]
                    except KeyError:
                        try:
                            process = Process.objects.get(name_id=process_name_id)
                            process_items[process_name_id] = process
                        except Process.DoesNotExist:
                            process = None

                    if not process:
                        raise APIException('Process from config not found.')

                    try:
                        prop_item = prop_items[prop]
                    except KeyError:
                        prop_item = Property.objects.get(name_id=prop)
                        prop_items[prop] = prop_item

                    data_range = get_feature_nn_from_list(
                        nn_feature_ranges,
                        item,
                        prop_item.id,
                        process.id
                    )

                    if data_range:
                        if value_duration is None:
                            value_duration = get_first_observation_duration(
                                pt_range=pt_range_z,
                                observed_property=prop_item,
                                observation_provider_model=provider_model,
                                feature_of_interest=item,
                                process=process
                            )

                        feature_time_slots = get_empty_slots(t, data_range)

                        get_observations_func = partial(
                            get_observations,
                            feature_time_slots,
                            prop_item,
                            provider_model,
                            item,
                            process,
                            t)

                        ts = get_timeseries(
                            phenomenon_time_range=data_range,
                            num_time_slots=len(feature_time_slots),
                            get_observations=get_observations_func
                        )

                        if time_slots is None:
                            time_slots = feature_time_slots

                        if ts['phenomenon_time_range'].lower is not None:
                            if not phenomenon_time_from or phenomenon_time_from > ts['phenomenon_time_range'].lower:
                                phenomenon_time_from = ts['phenomenon_time_range'].lower

                                if USE_DYNAMIC_TIMESLOTS is True:
                                    if time_slots != feature_time_slots:
                                        for idx in range(len(feature_time_slots)):
                                            slot = feature_time_slots[idx]
                                            if slot.lower == time_slots[0].lower and slot.upper == \
                                                    time_slots[0].upper:
                                                time_slots = feature_time_slots[:idx] + time_slots
                                                break

                        if ts['phenomenon_time_range'].upper is not None:
                            if not phenomenon_time_to or phenomenon_time_to > ts['phenomenon_time_range'].upper:
                                phenomenon_time_to = ts['phenomenon_time_range'].upper

                        rounded_ar = list(map((lambda val: round(val, ROUND_DECIMAL_SPACES) if val is not None else None),
                                           ts['property_anomaly_rates']))

                        feature_prop_dict = {
                            'values': ts['property_values'],
                            'anomaly_rates': rounded_ar,
                            'phenomenon_time_from': ts['phenomenon_time_range'].lower,
                            'phenomenon_time_to': ts['phenomenon_time_range'].upper,
                            'value_index_shift': None
                        }

                        content[prop] = feature_prop_dict

                        if len(ts['property_values']) > 0:
                            has_values = True

                feature_id = path[0] + \
                    "." + \
                    feature_of_interest_model.__name__ + \
                    ":" + \
                    str(item.id_by_provider)

                if has_values:
                    f = TimeSeriesFeature(
                        id=feature_id,
                        id_by_provider=item.id_by_provider,
                        name=item.name,
                        geometry=item.geometry,
                        content=content
                    )
                    time_series_list.append(f)


            #print(grouped)

        for item in time_series_list:
            if phenomenon_time_from:
                for item_prop in item.content:
                    item_prop_from = item.content[item_prop]['phenomenon_time_from']

                    if phenomenon_time_from and item_prop_from:
                        value_index_shift = get_index_shift(time_slots, phenomenon_time_from, item_prop_from)
                        item.content[item_prop]['value_index_shift'] = value_index_shift
                    else:
                        item.content[item_prop]['value_index_shift'] = None

                    try:
                        del item.content[item_prop]['phenomenon_time_from']
                    except KeyError:
                        pass

                    try:
                        del item.content[item_prop]['phenomenon_time_to']
                    except KeyError:
                        pass

        if len(time_series_list) == 0:
            value_frequency = None

        response_data = {
            'phenomenon_time_from': phenomenon_time_from,
            'phenomenon_time_to': phenomenon_time_to,
            'value_frequency': value_frequency,
            'value_duration': value_duration,
            'feature_collection': time_series_list,
            'properties': param_properties
        }

        results = TimeSeriesSerializer(response_data).data
        return Response(results)
