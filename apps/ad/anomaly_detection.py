from django.conf import settings
from apps.common.models import Process

import pytz
import time
from psycopg2.extras import DateTimeTZRange
from dateutil.parser import parse

from luminol.anomaly_detector import AnomalyDetector

stations_def = ('11359201', '11359196', '11359205',
                '11359192', '11359202', '11359132')


def get_timeseries(observed_property, observation_provider_model, feature_of_interest, phenomenon_time_range=DateTimeTZRange("2018-01-01 00:00:00+01", "2019-01-01 00:00:00+01")):
    frequency = settings.APPLICATION_MC.PROPERTIES[observed_property.name_id]["value_frequency"]
    process = Process.objects.get(
        name_id=settings.APPLICATION_MC.PROPERTIES[observed_property.name_id]["process"])
    observation_model_name = f"{observation_provider_model.__module__}.{observation_provider_model.__name__}"
    
    print(observed_property, process, feature_of_interest)

    obss = observation_provider_model.objects.raw('''SELECT * FROM ala_observation WHERE
        lower(phenomenon_time_range) BETWEEN %s AND %s AND
        mod(cast(extract(epoch from lower(phenomenon_time_range)) as int), %s)=0 AND
        mod(cast(extract(epoch from upper(phenomenon_time_range)) as int) - cast(extract(epoch from lower(phenomenon_time_range)) as int), %s)=0 AND
        observed_property_id=%s AND
        procedure_id=%s AND
        feature_of_interest_id=%s''', [phenomenon_time_range.lower, phenomenon_time_range.upper, frequency, frequency, observed_property.id, process.id, feature_of_interest.id])

    anomalyScore = anomaly_detect(obss)

    result = {
        'phenomenon_time_range': phenomenon_time_range,
        'value_frequency': frequency,
        'property_values': obss,
        'property_anomaly_rates': anomalyScore,
    }

    return result

def anomaly_detect(list_obss, detector_method='default_detector'):
    results_dic = dict()
    for line in list_obss:
        results_dic[time.mktime(line.phenomenon_time_range.lower.astimezone(
            pytz.utc).timetuple())] = None if line.result == None else float(line.result)

    my_detector = AnomalyDetector(
        results_dic, None, False, None, None, detector_method, None, None, None)
    anomalies = my_detector.get_anomalies()
    if anomalies:
        time_period = anomalies[0].get_time_window()

    #TODO: the anomaly point

    score = my_detector.get_all_scores()

    return list(score.itervalues())
