from django.test import TestCase
from apps.processing.ala.models import SamplingFeature, Observation
from django.contrib.gis.geos import GEOSGeometry, Point
from apps.common.models import Process, Property
from psycopg2.extras import DateTimeTZRange
from datetime import timedelta, datetime
from apps.ad.anomaly_detection import get_timeseries

from apps.mc.serializers import PropertySerializer, TimeSeriesSerializer
from apps.common.models import Property
from apps.mc.models import TimeSeriesFeature
from apps.ad.anomaly_detection import get_timeseries
from rest_framework import status
from rest_framework.test import APITestCase
import json

from django.test import Client

from django.contrib.auth.models import AnonymousUser, User

URL_TIMESERIES = '/api/v1/timeseries/?name_id=air_temperature&phenomenon_date_from=2018-06-15&phenomenon_date_to=2018-06-15'

time_range_boundary = '[)'
time_from = datetime(2018, 6, 15, 00, 00, 00)
date_time_range = DateTimeTZRange(
    time_from,
    time_from + timedelta(hours=24),
    time_range_boundary
)


def get_time_series_test():
    station = SamplingFeature.objects.get(name="Brno")
    prop = Property.objects.get(name_id='air_temperature')
    time_range = date_time_range

    return get_timeseries(
        observed_property=prop,
        observation_provider_model=Observation,
        feature_of_interest=station,
        phenomenon_time_range=time_range
    )


class SamplingFeatureTestCase(APITestCase):
    def setUp(self):

        am_process = Process.objects.create(
            name_id='apps.common.aggregate.arithmetic_mean',
            name='arithmetic mean'
        )

        station = SamplingFeature.objects.create(
            id_by_provider="11359201",
            name="Brno",
            geometry=GEOSGeometry('POINT (1847520.94 6309563.27)', srid=3857)
        )

        at_prop = Property.objects.create(
            name_id='air_temperature',
            name='air temperature',
            unit='°C',
            default_mean=am_process
        )

        time_from = datetime(2018, 6, 14, 13, 00, 00)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station,
            procedure=am_process,
            result=1.5,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(hours=1),
                time_range_boundary
            )
        )

        time_from = datetime(2018, 6, 15, 10, 00, 00)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station,
            procedure=am_process,
            result=1,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(hours=1),
                time_range_boundary
            )
        )

        time_from = datetime(2018, 6, 15, 11, 00, 00)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station,
            procedure=am_process,
            result=1000,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(hours=1),
                time_range_boundary
            )
        )

        time_from = datetime(2018, 6, 15, 12, 00, 00)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station,
            procedure=am_process,
            result=1.5,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(hours=1),
                time_range_boundary
            )
        )

        time_from = datetime(2018, 6, 16, 13, 00, 00)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station,
            procedure=am_process,
            result=1.5,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(hours=1),
                time_range_boundary
            )
        )

    # Output for database created by test setup
    '''
       {
           'phenomenon_time_range': DateTimeTZRange(
               datetime.datetime(2018, 6, 15, 11, 0), //od konce mereni - konec je start +1h
               datetime.datetime(2018, 6, 15, 14, 0), //od konce posledniho mereni +1h - protoze posledni interval uz tam nespada ')'
               '[)' //zacatek spada, konec ne
           ), 
           'value_frequency': 3600,  //1h
           'property_values': [
               Decimal('1.000'), 
               Decimal('1000.000'), 
               Decimal('1.500')], 
           'property_anomaly_rates': [
               0.0, 
               1.697480910372832, 
               0.9625824050649426
           ]
       }
       
       {
       'phenomenon_time_from': '2018-06-15T11:00:00+01:00', 
       'phenomenon_time_to': '2018-06-15T14:00:00+01:00', 
       'value_frequency': 3600, 
       'feature_collection': 
        OrderedDict([
            ('type', 'FeatureCollection'), 
            ('features', [OrderedDict([
                ('id', 4), ('type', 'Feature'), 
                ('geometry', GeoJsonDict([
                    ('type', 'Point'), 
                    ('coordinates', [1847520.94, 6309563.27])
                ])), 
                ('properties', OrderedDict([
                    ('id_by_provider', '11359201'), 
                    ('name', 'Brno'), 
                    ('value_index_shift', 0), 
                    ('property_values', [Decimal('1.00000'), Decimal('1000.00000'), Decimal('1.50000')]), 
                    ('property_anomaly_rates', [Decimal('0.00000'), Decimal('1.69748'), Decimal('0.96258')])
                ])
            )]
            ])
        ])}

       '''

    def test_response_status(self) :
        response = self.client.get(URL_TIMESERIES)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_property_values_length_equals_anomaly_rates(self):
        response = self.client.get(URL_TIMESERIES)
        data = response.data
        fc = data['feature_collection']
        features = fc['features']

        for f in features:
            properties = f.get('properties', None)
            property_values = properties.get('property_values', None)
            property_anomaly_rates = properties.get('property_anomaly_rates', None)
            self.assertEquals(len(property_values), len(property_anomaly_rates))

    def test_feature_output(self):
        response = self.client.get(URL_TIMESERIES, format='json')
        data = response.data
        print('data: ', data)

        fc = data['feature_collection']
        features = fc['features']

        for f in features:
            properties = f.get('properties', None)

            geom = f.get('geometry', None)
            type = geom.get('type', None)
            coordinates = geom.get('coordinates', None)
            id_by_provider = properties.get('id_by_provider', None)

            self.assertEquals(id_by_provider, '11359201')
            self.assertEquals(type, 'Point')
            self.assertEquals(len(coordinates), 2)
            self.assertEquals(coordinates[0], 1847520.94)
            self.assertEquals(coordinates[1], 6309563.27)

    '''
    def test_bbox_param_data(self):
        self.assertEquals(True, False)

    def test_bbox_param_no_data_in_area(self):
        self.assertEquals(True, False)
    '''




    '''
    def test_create_process(self):
        c = Client()
        response = c.get('/api/v1/properties/')
        print('response.status_code: ', response.status_code)
        print('response.content: ', response.content)
        self.assertEqual(True, False)
    '''


    '''    
    TODO
    
    for feature of OUT.feature_collection
        # feature.property_values.length === feature.property_anomaly_rates.length
        # feature.property_values.length + feature.value_index_shift <= (
            phenomenon_time_to::seconds - phenomenon_time_from::seconds) / value_frequency
    
    # OUT.phenomenon_time_from::seconds % OUT.value_frequency === 0
    
    # (OUT.phenomenon_time_to::seconds - OUT.phenomenon_time_from::seconds) % OUT.value_frequency 
    === 0

    '''
