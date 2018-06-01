from django.conf import settings
from apps.common.models import Process
from psycopg2.extras import DateTimeTZRange

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

    obs_reduced = {x.phenomenon_time_range.lower.timestamp(): x.result for x in obss}

    if len(obs_reduced.keys()) == 0:
        return {
            'phenomenon_time_range': DateTimeTZRange(),
            'value_frequency': None,
            'property_values': [],
            'property_anomaly_rates': [],
        }

    result_time_range = DateTimeTZRange(
        min(list(obs_reduced.keys())),
        max(list(obs_reduced.keys()))
    )

    while obs_reduced and obs_reduced[result_time_range.lower] is None:
        del obs_reduced[result_time_range.lower]
        if obs_reduced:
            result_time_range = DateTimeTZRange(
                min(list(obs_reduced.keys())),
                result_time_range.upper
            )
    while obs_reduced and obs_reduced[result_time_range.upper] is None:
        del obs_reduced[result_time_range.upper]
        if obs_reduced:
            result_time_range = DateTimeTZRange(
                result_time_range.lower,
                max(list(obs_reduced.keys()))
            )
    
    if len(obs_reduced.keys()) == 0:
        return {
            'phenomenon_time_range': DateTimeTZRange(),
            'value_frequency': None,
            'property_values': [],
            'property_anomaly_rates': [],
        }

    (anomalyScore, anomalyPeriod) = anomaly_detect(obs_reduced)

    dt = result_time_range.upper - result_time_range.lower

    print(dt, frequency, dt/frequency, range(1, int(dt/frequency)))

    for i in range(1, int(dt/frequency)):
        t = result_time_range.lower + i * frequency
        if t not in obs_reduced or obs_reduced[t] is None:
            print(i, t)
            obs_reduced[t] = None
            anomalyScore.insert(i, None)

    result = {
        'phenomenon_time_range': phenomenon_time_range,
        'value_frequency': frequency,
        'property_values': obs_reduced.values(),
        'property_anomaly_rates': anomalyScore,
    }

    return result


def anomaly_detect(observations, detector_method='bitmap_detector'):
    time_period = None

    my_detector = AnomalyDetector(observations, algorithm_name=detector_method)
    anomalies = my_detector.get_anomalies()

    if anomalies:
        time_period = anomalies[0].get_time_window()

    #TODO: the anomaly point

    score = my_detector.get_all_scores()

    return (list(score.itervalues()), time_period)
