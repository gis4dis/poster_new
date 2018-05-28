import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.processing.ala.util import util
from psycopg2.extras import DateTimeTZRange
from dateutil.parser import parse
from dateutil import relativedelta
from datetime import date, timedelta
from apps.common.models import Process, Property
from apps.processing.ala.models import SamplingFeature, Observation
from luminol.anomaly_detector import AnomalyDetector
from datetime import datetime
import pytz
import time

logger = logging.getLogger(__name__)

stations_def = ('11359201', '11359196', '11359205',
                '11359192', '11359202', '11359132')


def get_timeseries(prop="air_temperature", observation_provider_model="apps.processing.ala.Observation", feature_of_interest='11359201', time_range=DateTimeTZRange("2018-01-01 00:00:00+01", "2019-01-01 00:00:00+01")):
    time_range_field = "phenomenon_time_range"

    proc = settings.APPLICATION_MC.PROPERTIES[prop]["process"]
    frequency = settings.APPLICATION_MC.PROPERTIES[prop]["value_frequency"]
    feature = SamplingFeature.objects.get(id_by_provider=feature_of_interest)
    observed_property = Property.objects.get(name_id=prop)
    procedure = Process.objects.get(name_id=proc)
    
    print(observed_property, procedure, feature)

    obss = Observation.objects.raw('''SELECT * FROM ala_observation WHERE
        lower(phenomenon_time_range) BETWEEN %s AND %s AND
        mod(cast(extract(epoch from lower(phenomenon_time_range)) as int), %s)=0 AND
        mod(cast(extract(epoch from upper(phenomenon_time_range)) as int) - cast(extract(epoch from lower(phenomenon_time_range)) as int), %s)=0 AND
        observed_property_id=%s AND
        procedure_id=%s AND
        feature_of_interest_id=%s''', [time_range.lower, time_range.upper, frequency, frequency, observed_property.id, procedure.id, feature.id])

    # obss = Observation.objects.filter(
    #     # phenomenon_time_range__starts_with=F("phenomenon_time_range")[
    #     #     0] - F("phenomenon_time_range")[0] % frequency,
    #     # phenomenon_time_range__ends_with=F("phenomenon_time_range")[1] - (
    #     #     F("phenomenon_time_range")[1] - F("phenomenon_time_range")[0]) % frequency,
    #     feature_of_interest=feature_of_interest,
    #     observed_property=Property.objects.get(name_id=prop),
    #     procedure=Process.objects.get(name_id=procedure)
    # )

    anomalyScore = anomaly_detect(obss)

    result = {
        'phenomenon_time_range': time_range,
        'value_frequency': frequency,
        'property_values': obss,
        'property_anomaly_rates': anomalyScore,
    }

    return result

def anomaly_detect(list_obss, detector_method='default_detector'):
    results_dic = dict()
    for line in list_obss:
        results_dic[time.mktime(line.phenomenon_time_range.lower.astimezone(
            pytz.utc).timetuple())] = float(line.result)

    my_detector = AnomalyDetector(
        results_dic, None, False, None, None, detector_method, None, None, None)
    anomalies = my_detector.get_anomalies()
    if anomalies:
        time_period = anomalies[0].get_time_window()

    #TODO: the anomaly point

    score = my_detector.get_all_scores()

    return list(score.itervalues())