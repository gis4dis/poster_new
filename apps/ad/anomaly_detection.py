from django.conf import settings
from apps.common.models import Process
from datetime import datetime
from psycopg2.extras import DateTimeTZRange

from luminol.anomaly_detector import AnomalyDetector

def get_timeseries(observed_property, observation_provider_model, feature_of_interest, phenomenon_time_range):
    frequency = settings.APPLICATION_MC.PROPERTIES[observed_property.name_id]["value_frequency"]
    process = Process.objects.get(
        name_id=settings.APPLICATION_MC.PROPERTIES[observed_property.name_id][observation_provider_model]["process"])
    observation_model_name = f"{observation_provider_model.__module__}.{observation_provider_model.__name__}"
    timezone = phenomenon_time_range.lower.tzinfo

    obss = observation_provider_model.objects.raw('''SELECT * FROM ala_observation WHERE
        %s @> phenomenon_time_range AND
        mod(cast(extract(epoch from lower(phenomenon_time_range)) as int), %s)=0 AND
        cast(extract(epoch from upper(phenomenon_time_range)) as int) - cast(extract(epoch from lower(phenomenon_time_range)) as int)=%s AND
        observed_property_id=%s AND
        procedure_id=%s AND
        feature_of_interest_id=%s''', [f'[{phenomenon_time_range.lower},{phenomenon_time_range.upper})', frequency, frequency, observed_property.id, process.id, feature_of_interest.id])

    debug = {x.phenomenon_time_range.lower: [x.result, x.phenomenon_time_range] for x in obss}

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

    #print(dt, frequency, dt/frequency, range(1, int(dt/frequency)))

    for i in range(1, int(dt/frequency)):
        t = result_time_range.lower + i * frequency
        if t not in obs_reduced or obs_reduced[t] is None:
            #print(i, t)
            obs_reduced[t] = None
            anomalyScore.insert(i, None)

    return {
        'phenomenon_time_range': DateTimeTZRange(datetime.fromtimestamp(result_time_range.lower).replace(tzinfo=timezone), datetime.fromtimestamp(result_time_range.upper).replace(tzinfo=timezone)),
        'value_frequency': frequency,
        'property_values': list(obs_reduced.values()),
        'property_anomaly_rates': anomalyScore,
    }

def anomaly_detect(observations, detector_method='bitmap_detector'):
    time_period = None

    my_detector = AnomalyDetector(observations, algorithm_name=detector_method)
    anomalies = my_detector.get_anomalies()

    if anomalies:
        time_period = anomalies[0].get_time_window()

    #TODO: the anomaly point

    score = my_detector.get_all_scores()

    return (list(score.itervalues()), time_period)
