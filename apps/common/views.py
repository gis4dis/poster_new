from importlib import import_module

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.gis.geos import Polygon
from rest_framework.exceptions import APIException
from django.conf import settings

from dateutil.parser import parse
from dateutil import relativedelta
from psycopg2.extras import DateTimeTZRange

from apps.common.serializers import PropertySerializer, TimeSeriesSerializer
from apps.common.models import Property, TimeSeriesFeature

from  apps.ad.anomaly_detection import get_timeseries


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


#TODO prehodit do nejakych timeutil, ktere uz nekde jsou apps.utils.time asi
#TODO kontrola dat, zachytavani erroru
def parse_date_range(from_string, to_string):
    if from_string:
        day_from = parse(from_string)

    if to_string:
        day_to = parse(to_string)
        day_to = day_to + relativedelta.relativedelta(days=1)

    time_range_boundary = '[]' if day_from == day_to else '[)'

    pt_range = DateTimeTZRange(
        day_from, day_to, time_range_boundary)

    return  pt_range, day_from, day_to


def float_bbox_param(value):
    try:
        float_val = float(value)
        return float_val
    except:
        raise APIException("BBOX param float conversion error: %s" % value)


#TODO ovalidovat, kontroly, ze min < max (opravit error messages)
def validate_bbox_values(bbox_array):
    if bbox_array[0] >= bbox_array[2]:
        raise APIException("BBOX minx is not < maxx")

    if bbox_array[1] >= bbox_array[3]:
        raise APIException("BBOX miny is not < maxy")


#TODO zachytavani - tvorba polygonu, float()
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


class PropertyViewSet(viewsets.ReadOnlyModelViewSet):
    prop_names = settings.APPLICATION_MC.PROPERTIES.keys()
    queryset = Property.objects.filter(name_id__in=prop_names)
    serializer_class = PropertySerializer


#TODO refactoring
#TODO otestovat vice provideru v ramci jedne charakteristiky v configu
#TODO kontrola vstupu - timeFrom < timeTo, ...
# http://localhost:8000/api/v1/timeseries?name_id=water_level&phenomenon_date_from=2017-01-20&phenomenon_date_to=2017-01-27&bbox=1826997.8501,6306589.8927,1846565.7293,6521189.3651
# http://localhost:8000/api/v1/timeseries?name_id=water_level&phenomenon_date_from=2017-01-20&phenomenon_date_to=2017-01-27
# http://localhost:8000/api/v1/timeseries?name_id=air_temperature&phenomenon_date_from=2017-01-20&phenomenon_date_to=2017-01-27&bbox=1826997.8501,6306589.8927,1846565.7293,6521189.3651
# http://localhost:8000/api/v1/timeseries?name_id=air_temperature&phenomenon_date_from=2018-01-20&phenomenon_date_to=2018-09-27

@api_view(['GET'])
def time_series_list(request):
    '''
    #SELECT *
    #FROM pmo_watercoursestation AS a
    #WHERE ST_Intersects(geometry, ST_MakeEnvelope(1826997.8501,6306589.8927,1846565.7293,6521189.3651, 3857))
    '''

    if request.method == 'GET':

        if 'name_id' in request.GET:
            name_id = request.GET['name_id']
        else:
            raise APIException("Parameter name_id is required")

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

        if not (name_id in settings.APPLICATION_MC.PROPERTIES):
            raise APIException("name_id not found in config")

        config_prop = settings.APPLICATION_MC.PROPERTIES[name_id]
        config_observation_providers = config_prop['observation_providers']
        value_frequency = config_prop['value_frequency']

        for key in config_observation_providers:
            time_series_list = []
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

            for item in all_features:
                ts_dict = get_timeseries(
                        observed_property=Property.objects.get(name_id=name_id),
                        observation_provider_model=provider_model,
                        feature_of_interest=item,
                        phenomenon_time_range=pt_range)

                print('ts_dict', ts_dict)

                f = TimeSeriesFeature(
                    id=item.id,
                    id_by_provider=item.id_by_provider,
                    name=item.name,
                    geometry=item.geometry,
                    property_values=ts_dict['property_values'], #[1, 2, 3],
                    property_anomaly_rates=ts_dict['property_anomaly_rates'] #[10, 11, 12]
                )
                time_series_list.append(f)

            response_data = {
                'phenomenon_time_from': day_from,
                'phenomenon_time_to': day_to,
                'value_frequency': value_frequency,
                'data':  time_series_list
            }

        results = TimeSeriesSerializer(response_data).data
        return Response(results)


class PropertyViewSet(viewsets.ReadOnlyModelViewSet):
    prop_names = settings.APPLICATION_MC.PROPERTIES.keys()
    queryset = Property.objects.filter(name_id__in=prop_names)
    serializer_class = PropertySerializer
