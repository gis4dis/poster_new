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
from apps.common.models import Property, Process, AbstractObservation
from apps.common.models import Topic
from apps.mc.models import TimeSeriesFeature
from apps.common.models import TimeSlots
from apps.mc.api.serializers import PropertySerializer, TimeSeriesSerializer, TopicSerializer, TimeSlotsSerializer
from apps.utils.time import UTC_P0100
from apps.common.util.util import generate_intervals, generate_n_intervals
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

'''

    get_topics(): list of topics
    get_property(topic): list of properties
    get_time_slots(topic, property): list of time slots
    get_features_of_interest(topic, property): list of features
    get_aggregating_process(topic, property, feature_of_interest): process
    get_observation_getter(topic, property, time_slots, feature_of_interest, phenomenon_time_range): observation_getter for get_timeseries method

'''


def get_topics():
    topics = settings.APPLICATION_MC.TOPICS.keys()
    return Topic.objects.filter(name_id__in=list(topics))


def get_property(topic):
    topic_param = topic.name_id
    topic = settings.APPLICATION_MC.TOPICS.get(topic_param)
    prop_names = list(topic['properties'].keys())
    queryset = Property.objects.filter(name_id__in=prop_names)
    return queryset


#TODO dodelat vstupni parametry
def get_time_slots(topic, property):
    queryset = TimeSlots.objects.all()
    return queryset


#TODO property - zvazit jestli ma cenu spojovat s view
def get_features_of_interest(topic, properties, geom_bbox = None):
    topic = topic.name_id
    topic_config = settings.APPLICATION_MC.TOPICS.get(topic)
    out_features = []

    if not topic_config or not Topic.objects.filter(name_id=topic).exists():
        raise APIException('Topic not found.')

    model_props = {}

    properties_config = topic_config['properties']

    if topic_config:
        for prop in properties:
            prop_config = properties_config.get(prop.name_id)
            op = prop_config['observation_providers']

            for provider in op:
                if provider in model_props:
                    model_props[provider].append(prop.name_id)
                else:
                    model_props[provider] = [prop.name_id]

    for model in model_props:
        provider_module, provider_model, error_message = import_models(model)
        if error_message:
            raise APIException("Importing error - %s : %s" % (model, error_message))

        path = model.rsplit('.', 1)
        provider_module = import_module(path[0])
        provider_model = getattr(provider_module, path[1])

        feature_of_interest_model = provider_model._meta.get_field(
            'feature_of_interest').remote_field.model

        if geom_bbox:
            all_features = feature_of_interest_model.objects.filter(geometry__intersects=geom_bbox)
        else:
            all_features = feature_of_interest_model.objects.all()
            '''
            obs_model = all_features[0]._meta.get_fields()[0].remote_field.model
            
            op_name = obs_model.__module__
            if op_name is None or op_name == str.__class__.__module__:
                op_name = obs_model.__class__.__name__
            else:
                op_name = op_name + '.' + obs_model.__name__

            print('op_name: ', op_name)
            '''
            print(all_features)

        return out_features.extend(all_features)


def get_aggregating_process(topic, property, feature_of_interest):
    topic = topic.name_id
    topic_config = settings.APPLICATION_MC.TOPICS.get(topic)

    obs_model = feature_of_interest._meta.get_fields()[0].remote_field.model

    op_name = obs_model.__module__
    if op_name is None or op_name == str.__class__.__module__:
        op_name = obs_model.__class__.__name__
    else:
        op_name = op_name + '.' + obs_model.__name__

    prop_config = topic_config['properties'].get(property.name_id)['observation_providers'].get(op_name)

    return prop_config