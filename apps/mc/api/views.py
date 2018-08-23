from importlib import import_module

from dateutil import relativedelta
from dateutil.parser import parse
from django.conf import settings
from django.contrib.gis.geos import Polygon
from psycopg2.extras import DateTimeTZRange
from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from apps.ad.anomaly_detection import get_timeseries
from apps.common.models import Property, Process
from apps.common.models import Topic
from apps.mc.api.serializers import PropertySerializer, TimeSeriesSerializer, TopicSerializer
from apps.mc.models import TimeSeriesFeature

from apps.mc import settings_v2


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


def validate_time_series_feature(item, time_series_from, time_series_to, value_frequency):
    if time_series_from and time_series_to:
        time_series_from_s = int(round(time_series_from.timestamp() * 1000))
        time_series_to_s = int(round(time_series_to.timestamp() * 1000))

        if len(item.property_values) != len(item.property_anomaly_rates):
            raise APIException(
                "Error: feature.property_values.length !== feature.property_anomaly_rates.length")

        if time_series_from_s % value_frequency != 0:
            raise APIException(
                "Error: OUT.phenomenon_time_from::seconds % OUT.value_frequency !== 0")

        if (time_series_to_s - time_series_from_s) % value_frequency != 0:
            raise APIException(
                "Error: (OUT.phenomenon_time_to::seconds - OUT.phenomenon_time_from::seconds) % OUT.value_frequency != 0")

        values_max_count = (time_series_to - time_series_from).total_seconds() / value_frequency

        if (len(item.property_values) + item.value_index_shift) > values_max_count:
            raise APIException(
                "Error: feature.property_values.length + feature.value_index_shift > (phenomenon_time_to::seconds - phenomenon_time_from::seconds) / value_frequency")



class PropertyViewSet(viewsets.ViewSet):

    def list(self, request):
        if 'topic' in request.GET:
            topic_param = request.GET['topic']
            topic = settings.APPLICATION_MC.TOPICS.get(topic_param)

            if topic:
                prop_names = list(topic['properties'].keys())
            else:
                prop_names = []

            queryset = Property.objects.filter(name_id__in=prop_names)
            serializer = PropertySerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            raise APIException("Parameter topic is required")


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    topics = settings.APPLICATION_MC.TOPICS.keys()
    queryset = Topic.objects.filter(name_id__in=list(topics))
    serializer_class = TopicSerializer


#TODO otestovat vice provideru v ramci jedne charakteristiky v configu
# http://localhost:8000/api/v1/timeseries?name_id=water_level&phenomenon_date_from=2017-01-20&phenomenon_date_to=2017-01-27&bbox=1826997.8501,6306589.8927,1846565.7293,6521189.3651
# http://localhost:8000/api/v1/timeseries?name_id=water_level&phenomenon_date_from=2017-01-20&phenomenon_date_to=2017-01-27
# http://localhost:8000/api/v1/timeseries?name_id=air_temperature&phenomenon_date_from=2017-01-20&phenomenon_date_to=2017-01-27&bbox=1826997.8501,6306589.8927,1846565.7293,6521189.3651
# http://localhost:8000/api/v1/timeseries?name_id=air_temperature&phenomenon_date_from=2018-01-20&phenomenon_date_to=2018-09-27

# http://localhost:8000/api/v1/timeseries?topic=drought&properties=air_temperature,ground_air_temperature&phenomenon_date_from=2018-01-20&phenomenon_date_to=2018-09-27
class TimeSeriesViewSet(viewsets.ViewSet):

    def list(self, request):
        if 'topic' in request.GET:
            topic = request.GET['topic']
        else:
            raise APIException('Parameter topic is required')

        #TODO
        print('TODO implementace nacteni properties z topicu')
        print('TODO validate neexistujici props,...')
        print('validace oproti DB')

        if 'properties' in request.GET:
            properties_string = request.GET['properties']
        else:
            raise APIException("Parameter properties is required")

        param_properties = parse_properties(properties_string)

        if 'phenomenon_date_from' in request.GET:
            phenomenon_date_from = request.GET['phenomenon_date_from']
        else:
            raise APIException("Parameter phenomenon_date_from is required")

        if 'phenomenon_date_to' in request.GET:
            phenomenon_date_to = request.GET['phenomenon_date_to']
        else:
            raise APIException("Parameter phenomenon_date_to is required")

        pt_range, day_from, day_to = parse_date_range(phenomenon_date_from, phenomenon_date_to)

        geom_bbox = None
        if 'bbox' in request.GET:
            bbox = request.GET['bbox']
            geom_bbox = parse_bbox(bbox)

        topic_config = settings.APPLICATION_MC.TOPICS.get(topic)

        model_props = {}

        if topic_config:
            properties = topic_config['properties']
            for prop in param_properties:
                prop_config = properties.get(prop)
                if not prop_config:
                    raise APIException('Property: ' + prop + ' does not exist in config')

                op = prop_config['observation_providers']

                for provider in op:
                    if provider in model_props:
                        model_props[provider].append(prop)
                    else:
                        model_props[provider] = [prop]
        else:
            raise APIException('Topic in configuration not found.')

        time_series_list = []
        phenomenon_time_from = None
        phenomenon_time_to = None
        value_frequency = topic_config['value_frequency']

        for key in model_props:

            provider_module, provider_model, error_message = import_models(key)
            if error_message:
                raise APIException("Importing error - %s : %s" % (key, error_message))

            path = key.rsplit('.', 1)
            provider_module = import_module(path[0])
            provider_model = getattr(provider_module, path[1])

            feature_of_interest_model = provider_model._meta.get_field('feature_of_interest').remote_field.model

            if geom_bbox:
                all_features = feature_of_interest_model.objects.filter(geometry__intersects=geom_bbox)
            else:
                all_features = feature_of_interest_model.objects.all()

            observation_provider_model_name = f"{provider_model.__module__}.{provider_model.__name__}"

            for item in all_features:
                content = {}

                f_phenomenon_time_from = None
                f_phenomenon_time_to = None

                for prop in model_props[key]:
                    prop_config = topic_config['properties'][prop]

                    process = Process.objects.get(
                        name_id=prop_config['observation_providers'][
                            observation_provider_model_name]["process"])

                    ts = get_timeseries(
                        observed_property=Property.objects.get(name_id=prop),
                        observation_provider_model=provider_model,
                        feature_of_interest=item,
                        phenomenon_time_range=pt_range,
                        process=process,
                        frequency=value_frequency
                    )

                    if ts['phenomenon_time_range'].lower is not None:
                        if not phenomenon_time_from or phenomenon_time_from > ts['phenomenon_time_range'].lower:
                            phenomenon_time_from = ts['phenomenon_time_range'].lower

                    if ts['phenomenon_time_range'].upper is not None:
                        if not phenomenon_time_to or phenomenon_time_to > ts['phenomenon_time_range'].upper:
                            phenomenon_time_to = ts['phenomenon_time_range'].upper

                    if ts['phenomenon_time_range'].lower is not None:
                        if not f_phenomenon_time_from or f_phenomenon_time_from > ts['phenomenon_time_range'].lower:
                            f_phenomenon_time_from = ts['phenomenon_time_range'].lower

                    if ts['phenomenon_time_range'].upper is not None:
                        if not f_phenomenon_time_to or f_phenomenon_time_to > ts['phenomenon_time_range'].upper:
                            f_phenomenon_time_to = ts['phenomenon_time_range'].upper

                    if not value_frequency:
                        value_frequency = ts['value_frequency']

                    feature_prop_dict = {
                        'values': ts['property_values'],
                        'anomaly_rates': ts['property_anomaly_rates'],
                        'phenomenon_time_from': ts['phenomenon_time_range'].lower,
                        'phenomenon_time_to': ts['phenomenon_time_range'].upper,
                        'value_index_shift': 'TODO'
                    }

                    content[prop] = feature_prop_dict

                feature_id = path[0] +\
                             "." +\
                             feature_of_interest_model.__name__ +\
                             ":" +\
                             str(item.id_by_provider)

                f = TimeSeriesFeature(
                    id=feature_id,
                    id_by_provider=item.id_by_provider,
                    name=item.name,
                    geometry=item.geometry,
                    content=content
                )
                time_series_list.append(f)

        for item in time_series_list:
            if phenomenon_time_from:

                for item_prop in item.content:
                    item_prop_from = item.content[item_prop]['phenomenon_time_from']

                    if phenomenon_time_from and item_prop_from:
                        diff = phenomenon_time_from - item_prop_from
                        value_index_shift = round(abs(diff.total_seconds()) / value_frequency)
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


                #TODO
                print('TODO validation')
                #validate_time_series_feature(item, phenomenon_time_from, phenomenon_time_to, value_frequency)

        response_data = {
            'phenomenon_time_from': phenomenon_time_from,
            'phenomenon_time_to': phenomenon_time_to,
            'value_frequency': value_frequency,
            'feature_collection': time_series_list
        }

        results = TimeSeriesSerializer(response_data).data
        return Response(results)
