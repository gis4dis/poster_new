from apps.processing.ala.models import SamplingFeature, Observation
from django.contrib.gis.geos import GEOSGeometry
from apps.common.models import Process
from psycopg2.extras import DateTimeTZRange
from datetime import timedelta, datetime
from django.conf import settings

from apps.common.models import Property, Topic, TimeSlots
from apps.ad.anomaly_detection import get_timeseries
from rest_framework import status
from rest_framework.test import APITestCase
import dateutil.parser
import pytz
from apps.mc.tasks import import_time_slots_from_config

utc = pytz.UTC

NAME_ID = 'name_id=air_temperature'
DATE_FROM = '&phenomenon_date_from=2018-06-15'
DATE_TO = '&phenomenon_date_to=2018-06-15'
TIME_SLOT_10H = '&time_slots=10_hour_slot'
TIME_SLOT_24H = '&time_slots=24_hour_slot'

TOPIC_NAME = 'drought'
TOPIC_NAME_NOT_EXISTS = 'xxxx'

URL_TIMESERIES = '/api/v2/timeseries/?topic=' + TOPIC_NAME + DATE_FROM + DATE_TO
URL_TIMESERIES_TOPIC_NOT_EXISTS = '/api/v2/timeseries/?topic=' + TOPIC_NAME_NOT_EXISTS + DATE_FROM + DATE_TO
URL_TIMESERIES_TIME_SLOTS_NOT_EXISTS = '/api/v2/timeseries/?topic=' + TOPIC_NAME + DATE_FROM + DATE_TO + TIME_SLOT_10H
URL_TIMESERIES_TIME_SLOTS_24H = '/api/v2/timeseries/?topic=' + TOPIC_NAME + DATE_FROM + '&phenomenon_date_to=2018-06-17' + TIME_SLOT_24H

URL_TIMESERIES_30 = '/api/v2/timeseries/?topic=' + TOPIC_NAME + '&phenomenon_date_from=2018-06-16' + '&phenomenon_date_to=2018-06-16' + '&time_slots=30_days_daily'
#URL_TIMESERIES_30 = '/api/v2/timeseries/?topic=drought&properties=air_temperature&phenomenon_date_from=2018-06-15&phenomenon_date_to=2018-06-16&time_slots=30_days_daily'

DATE_FROM_ERROR = '&phenomenon_date_from=00000-06-15'
DATE_TO_ERROR = '&phenomenon_date_to=XXX'
URL_TIMESERIES_WRONG_DATE_FROM =  URL_TIMESERIES + DATE_FROM_ERROR + DATE_TO
URL_TIMESERIES_WRONG_DATE_TO = URL_TIMESERIES + DATE_FROM + DATE_TO_ERROR
URL_TIMESERIES_INTERVAL_NO_VALUES =  '/api/v2/timeseries/?topic=' + TOPIC_NAME + '&phenomenon_date_from=2000-06-15' + '&phenomenon_date_to=2000-06-15'

URL_TIMESERIES_BBOX = URL_TIMESERIES + '&bbox=1826997.8501,6306589.8927,1856565.7293,6521189.3651'
URL_TIMESERIES_BBOX_NO_DATA = URL_TIMESERIES + '&bbox=1826997.8501,6306589.8927,1836565.7293,6521189.3651'
URL_TIMESERIES_BBOX_WRONG_VALUES = URL_TIMESERIES + '&bbox=1856997.8501,6306589.8927,1836565.7293,6521189.3651'
URL_TIMESERIES_BBOX_MISSING_VALUES = URL_TIMESERIES + '&bbox=1856997.8501,6306589.8927,1836565.7293'

URL_PROPERTIES = '/api/v2/properties/?topic=' + TOPIC_NAME
URL_TOPICS = '/api/v2/topics/'


STATION_PROPS = {
    '11359201': {
        'id_by_provider': '11359201',
        'geom_type': 'Point',
        'name': 'Brno',
        'coordinates': [1847520.94, 6309563.27]
    },
    'brno2_id_by_provider': {
        'id_by_provider': 'brno2_id_by_provider',
        'geom_type': 'Point',
        'name': 'Brno2',
        'coordinates': [1847520.94, 6309563.27]
    }

}

time_range_boundary = '[)'
time_from = datetime(2018, 6, 15, 00, 00, 00)
date_time_range = DateTimeTZRange(
    time_from,
    time_from + timedelta(hours=24),
    time_range_boundary
)


def create_station(key):
    station_key = key
    props = STATION_PROPS[station_key]
    coordinates = props['coordinates']
    return SamplingFeature.objects.create(
        id_by_provider=props['id_by_provider'],
        name=props['name'],
        geometry=GEOSGeometry(
            props['geom_type'] + ' (' + str(coordinates[0]) + ' ' + str(coordinates[1]) + ')',
            srid=3857
        )
    )


def get_time_series_test():
    station = SamplingFeature.objects.get(name="Brno")
    prop = Property.objects.get(name_id='air_temperature')
    time_range = date_time_range
    topic_config = settings.APPLICATION_MC.TOPICS.get(TOPIC_NAME)
    process = Process.objects.get(name_id="apps.common.aggregate.arithmetic_mean")
    value_frequency = topic_config['value_frequency']

    return get_timeseries(
        observed_property=prop,
        observation_provider_model=Observation,
        feature_of_interest=station,
        phenomenon_time_range=time_range,
        process = process,
        frequency = value_frequency
    )


class RestApiTestCase(APITestCase):
    def setUp(self):

        Topic.objects.create(
            name_id='drought',
            name='drought'
        )

        am_process = Process.objects.create(
            name_id='apps.common.aggregate.arithmetic_mean',
            name='arithmetic mean'
        )

        station_key = '11359201'
        station = create_station(station_key)

        station_key = 'brno2_id_by_provider'
        station_2 = create_station(station_key)

        at_prop = Property.objects.create(
            name_id='air_temperature',
            name='air temperature',
            unit='°C',
            default_mean=am_process
        )

        Property.objects.create(
            name_id='ground_air_temperature',
            name='ground_air_temperature',
            unit='°C',
            default_mean=am_process
        )



        import_time_slots_from_config()
        t = TimeSlots.objects.get(name_id='1_hour_slot')
        t30 = TimeSlots.objects.get(name_id='30_days_daily')
        #"["2019-05-01 23:00:00+00","2019-05-31 23:00:00+00")"

        '''
        "["2019-04-30 23:00:00+00","2019-05-30 23:00:00+00")"
        "["2019-04-29 23:00:00+00","2019-05-29 23:00:00+00")"
        "["2019-04-28 23:00:00+00","2019-05-28 23:00:00+00")"
        "["2019-04-27 23:00:00+00","2019-05-27 23:00:00+00")"
        "["2019-04-26 23:00:00+00","2019-05-26 23:00:00+00")"
        '''

        time_from = datetime(2018, 6, 10, 23, 00, 00)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station_2,
            procedure=am_process,
            result=2,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(days=30),
                time_range_boundary
            ),
            time_slots=t30
        )

        time_from = datetime(2018, 6, 11, 23, 00, 00)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station_2,
            procedure=am_process,
            result=1.5,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(days=30),
                time_range_boundary
            ),
            time_slots=t30
        )

        time_from = datetime(2018, 6, 12, 23, 00, 00)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station_2,
            procedure=am_process,
            result=3.5,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(days=30),
                time_range_boundary
            ),
            time_slots=t30
        )

        time_from = datetime(2018, 6, 13, 23, 00, 00)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station_2,
            procedure=am_process,
            result=1.5,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(days=30),
                time_range_boundary
            ),
            time_slots=t30
        )

        time_from = datetime(2018, 6, 14, 23, 00, 00)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station_2,
            procedure=am_process,
            result=1.5,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(days=30),
                time_range_boundary
            ),
            time_slots=t30
        )

        time_from = datetime(2018, 6, 15, 23, 00, 00)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station_2,
            procedure=am_process,
            result=1.5,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(days=30),
                time_range_boundary
            ),
            time_slots=t30
        )


        time_from = datetime(2018, 6, 16, 23, 00, 00)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station_2,
            procedure=am_process,
            result=1.5,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(days=30),
                time_range_boundary
            ),
            time_slots=t30
        )

        time_from = datetime(2018, 6, 17, 23, 00, 00)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station_2,
            procedure=am_process,
            result=1.5,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(days=30),
                time_range_boundary
            ),
            time_slots=t30
        )

        time_from = datetime(2018, 6, 15, 11, 00, 00)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station_2,
            procedure=am_process,
            result=1.5,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(hours=1),
                time_range_boundary
            ),
            time_slots=t
        )

        time_from = datetime(2018, 6, 15, 12, 00, 00)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station_2,
            procedure=am_process,
            result=1.5,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(hours=1),
                time_range_boundary
            ),
            time_slots=t
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
            ),
            time_slots=t
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
            ),
            time_slots=t
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
            ),
            time_slots=t
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
            ),
            time_slots=t
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
            ),
            time_slots=t
        )

    def test_properties_response_status(self):
        response = self.client.get(URL_PROPERTIES)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_properties_response_content(self):
        response = self.client.get(URL_PROPERTIES)
        expected_response = [
            {"name_id": "air_temperature", "name": "air temperature", "unit": "°C" },
            {"name_id": "ground_air_temperature", "name": "ground_air_temperature", "unit": "°C"}
        ]
        self.assertEquals(response.data, expected_response)

    def test_topics_response_status(self):
        response = self.client.get(URL_TOPICS)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_topics_response_content(self):
        response = self.client.get(URL_TOPICS)
        expected_response = [
            {"name_id": "drought", "name": "drought"}
        ]
        self.assertEquals(response.data, expected_response)

    def test_timeseries_response_status(self):
        response = self.client.get(URL_TIMESERIES)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_timeseries_property_values_length_equals_anomaly_rates(self):
        response = self.client.get(URL_TIMESERIES)
        data = response.data
        fc = data['feature_collection']
        features = fc['features']
        props = data['properties']

        for f in features:
            properties = f.get('properties', None)
            for p in props:
                property = properties.get(p, None)
                if property:
                    property_values = property.get('values', None)
                    property_anomaly_rates = property.get('anomaly_rates', None)
                    self.assertEquals(len(property_values), len(property_anomaly_rates))

    def test_timeseries_feature_output(self):
        response = self.client.get(URL_TIMESERIES, format='json')
        data = response.data
        fc = data['feature_collection']
        features = fc['features']

        for f in features:
            props = f.get('properties', None)
            for p in props:
                self.assertIsNotNone(props.get(p, None))
            id = f.get('id', None)
            id_by_provider = id.split(':')[-1]

            geom = f.get('geometry', None)
            coordinates = geom.get('coordinates', None)
            geom_type = geom.get('type', None)

            props = STATION_PROPS[id_by_provider]
            self.assertEquals(id_by_provider, props['id_by_provider'])
            self.assertEquals(geom_type, 'Point')
            self.assertEquals(len(coordinates),  len(props['coordinates']))
            self.assertEquals(coordinates[0], props['coordinates'][0])
            self.assertEquals(coordinates[1], props['coordinates'][1])


    def test_timeseries_time_range_output(self):
        response = self.client.get(URL_TIMESERIES, format='json')
        data = response.data

        phenomenon_time_from = dateutil.parser.parse(data['phenomenon_time_from'])
        phenomenon_time_to = dateutil.parser.parse(data['phenomenon_time_to'])

        date_time_range_from_utc = date_time_range.lower.replace(tzinfo=utc)
        date_time_range_to_utc = date_time_range.upper.replace(tzinfo=utc)

        self.assertGreaterEqual(phenomenon_time_from, date_time_range_from_utc)
        self.assertLessEqual(phenomenon_time_to, date_time_range_to_utc)

    def test_timeseries_bbox_param_data(self):
        response = self.client.get(URL_TIMESERIES_BBOX, format='json')
        data = response.data
        fc = data['feature_collection']
        features = fc['features']
        self.assertNotEquals(len(features), 0)

    def test_timeseries_bbox_param_no_data_in_area(self):
        response = self.client.get(URL_TIMESERIES_BBOX_NO_DATA, format='json')
        data = response.data
        phenomenon_time_from = data['phenomenon_time_from']
        phenomenon_time_to = data['phenomenon_time_to']
        fc = data['feature_collection']
        features = fc['features']
        self.assertEquals(len(features), 0)
        self.assertEquals(phenomenon_time_from, None)
        self.assertEquals(phenomenon_time_to, None)

    def test_timeseries_interval_no_data(self):
        response = self.client.get(URL_TIMESERIES_INTERVAL_NO_VALUES, format='json')
        data = response.data
        fc = data['feature_collection']
        features = fc['features']
        self.assertEquals(len(features), 0)

    def test_timeseries_bbox_wrong_params(self):
        response = self.client.get(URL_TIMESERIES_BBOX_WRONG_VALUES, format='json')
        self.assertEquals(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_timeseries_bbox_missing_param(self):
        response = self.client.get(URL_TIMESERIES_BBOX_MISSING_VALUES, format='json')
        self.assertEquals(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_timeseries_phenomenon_date_from_wrong_param(self):
        response = self.client.get(URL_TIMESERIES_WRONG_DATE_FROM, format='json')
        self.assertEquals(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_timeseries_phenomenon_date_to_wrong_param(self):
        response = self.client.get(URL_TIMESERIES_WRONG_DATE_TO, format='json')
        self.assertEquals(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_timeseries_topic_not_exists(self):
        response = self.client.get(URL_TIMESERIES_TOPIC_NOT_EXISTS, format='json')
        self.assertEquals(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_timeseries_time_slots_24h(self):
        response = self.client.get(URL_TIMESERIES_TIME_SLOTS_24H, format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_timeseries_time_slots_not_exists(self):
        response = self.client.get(URL_TIMESERIES_TIME_SLOTS_NOT_EXISTS, format='json')
        self.assertEquals(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_30_days_timeslots(self):
        response = self.client.get(URL_TIMESERIES_30)
        data = response.data
        fc = data['feature_collection']
        features = fc['features']
        props = data['properties']

        for f in features:
            properties = f.get('properties', None)
            for p in props:
                property = properties.get(p, None)
                if property:
                    self.assertEquals(property.get('values', None), [2.000, 1.500, 3.500, 1.500, 1.500, 1.500])
                break
            break

