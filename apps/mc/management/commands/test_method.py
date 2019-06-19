import logging
from django.core.management.base import BaseCommand
from celery import chain

from apps.common.models import Property, Process
from apps.common.models import Topic
from apps.mc.models import TimeSeriesFeature
from apps.common.models import TimeSlots
from apps.mc.api.serializers import PropertySerializer, TimeSeriesSerializer, TopicSerializer, TimeSlotsSerializer
from apps.utils.time import UTC_P0100
from apps.common.util.util import generate_intervals, generate_n_intervals
from django.db.models import Max, Min
from django.db.models import F, Func, Q
from apps.processing.ala.models import SamplingFeature
logger = logging.getLogger(__name__)


from apps.mc.tasks import compute_aggregated_values, import_time_slots_from_config

from apps.mc.api.util import get_topics, get_property, get_time_slots, get_features_of_interest, get_aggregating_process

class Command(BaseCommand):

    def handle(self, *args, **options):
        t = Topic.objects.get(name_id='drought')
        p = Property.objects.filter(name_id='air_temperature')
        f = SamplingFeature.objects.get(id_by_provider='11359201')
        #print("AAAAAAAAAAAAAAAAA2", get_property(t))
        #print("get_time_slots: ", get_time_slots(None, None))
        #print('get_features_of_interest: ', get_features_of_interest(t, p))
        print('get_aggregating_process: ', get_aggregating_process(t, p[0], f))
