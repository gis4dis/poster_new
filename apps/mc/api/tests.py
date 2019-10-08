from apps.processing.ala.models import SamplingFeature, Observation
from django.contrib.gis.geos import GEOSGeometry
from apps.common.models import Process
from psycopg2.extras import DateTimeTZRange
from datetime import timedelta, datetime
from apps.common.models import Property, Topic, TimeSlots
from rest_framework.test import APITestCase
import pytz
from apps.mc.tasks import import_time_slots_from_config

from apps.mc.api.util import get_topics, get_property, get_time_slots, get_features_of_interest, get_aggregating_process, get_observation_getter

utc = pytz.UTC


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

class UtilTestCase(APITestCase):
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
            result=15,
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
            result=16,
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
            result=17,
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
            result=18,
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
            result=19,
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
            result=20,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(hours=1),
                time_range_boundary
            ),
            time_slots=t
        )

        time_from = datetime(2018, 6, 16, 00, 00, 00)
        Observation.objects.create(
            observed_property=at_prop,
            feature_of_interest=station,
            procedure=am_process,
            result=21,
            phenomenon_time_range=DateTimeTZRange(
                time_from,
                time_from + timedelta(hours=1),
                time_range_boundary
            ),
            time_slots=t
        )

    def test_properties_response_status(self):
        topics = get_topics()
        self.assertEquals(topics[0], Topic.objects.get(name_id='drought'))

    def test_get_property(self):
        t = Topic.objects.get(name_id='drought')
        property = get_property(t)
        self.assertEquals(property[0], Property.objects.get(name_id='air_temperature'))

    def test_get_time_slots(self):
        t = Topic.objects.get(name_id='drought')
        timeslots = get_time_slots(t)
        self.assertEquals(len(timeslots), 3)

    def test_get_feature_of_interest(self):
        t = Topic.objects.get(name_id='drought')
        p = Property.objects.get(name_id='air_temperature')
        features = get_features_of_interest(t, p)
        ids = []
        for f in features:
            ids.append(f.id_by_provider)
        self.assertEqual(ids, ['11359201', 'brno2_id_by_provider'])

    def test_get_aggregating_process(self):
        t = Topic.objects.get(name_id='drought')
        p = Property.objects.get(name_id='air_temperature')
        f = SamplingFeature.objects.get(id_by_provider='11359201')
        self.assertEqual(
            get_aggregating_process(t, p, f),
            Process.objects.get(name_id='apps.common.aggregate.arithmetic_mean')
        )

    #TODO - add more tests on data_getter
    def test_data_getter_function(self):
        t = Topic.objects.get(name_id='drought')
        p = Property.objects.get(name_id='air_temperature')
        f = SamplingFeature.objects.get(id_by_provider='11359201')
        ts = TimeSlots.objects.get(name_id='1_hour_slot')

        data_getter = get_observation_getter(
            topic=t,
            property=p,
            time_slots=ts,
            feature_of_interest=f,
            phenomenon_time_range=date_time_range
        )
        data = data_getter(0, 0)

        values = []
        for item in data:
            values.append(item.result)
        self.assertEqual(values, [18, 19, 20])



