import logging
from django.core.management.base import BaseCommand

from apps.common.models import Property
from apps.common.models import Topic
from apps.common.models import TimeSlots
from datetime import datetime

from apps.processing.ala.models import SamplingFeature
from psycopg2.extras import DateTimeTZRange

logger = logging.getLogger(__name__)
from apps.utils.time import UTC_P0100

from apps.mc.api.util import get_topics, get_property, get_time_slots, get_features_of_interest, get_aggregating_process, get_observation_getter

class Command(BaseCommand):
    def handle(self, *args, **options):
        t = Topic.objects.get(name_id='drought')
        p = Property.objects.get(name_id='air_temperature')
        f = SamplingFeature.objects.get(id_by_provider='11359201')
        ts = TimeSlots.objects.get(name_id="1_hour_slot")

        time_range_boundary = '[)'
        time_from = datetime(2019, 4, 13, 00, 00, 00).replace(tzinfo=UTC_P0100)
        time_to = datetime(2019, 4, 17, 00, 00, 00).replace(tzinfo=UTC_P0100)

        date_time_range = DateTimeTZRange(
            time_from,
            time_to,
            time_range_boundary
        )
        print('------get_topics------')
        print(get_topics())

        print('------get_property------')
        print(get_property(t))

        print('------get_time_slots------')
        print(get_time_slots(t))

        print('------get_features_of_interest------')
        print(get_features_of_interest(t, p))

        print('------get_aggregating_process------')
        print(get_aggregating_process(t, p, f))

        data_getter = get_observation_getter(
            topic=t,
            property=p,
            time_slots=ts,
            feature_of_interest=f,
            phenomenon_time_range=date_time_range
        )
        data = data_getter(0, 0)

        print('------get_observation_getter data------')
        print(data)
