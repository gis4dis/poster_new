from datetime import datetime
from psycopg2.extras import DateTimeTZRange
from luminol.anomaly_detector import AnomalyDetector


def observations_to_property_values(observations):
    return [obs.result for obs in observations]


def get_timeseries(
        phenomenon_time_range,
        num_time_slots,
        get_observations
):
    print('GT: ', phenomenon_time_range)
    observations = get_observations(3, 5)

    if not isinstance(observations, list):
        raise Exception('property_values should be array')

    if len(observations) == 0:
        return {
            'phenomenon_time_range': DateTimeTZRange(),
            'property_values': [],
            'property_anomaly_rates': [],
        }

    property_values = observations_to_property_values(observations)

    if len(observations) == 1:
        return {
            'phenomenon_time_range': phenomenon_time_range,
            'property_values': property_values,
            'property_anomaly_rates': [0],
        }

    obs_reduced = {}

    for i in range(len(observations)):
        obs_reduced[observations[i].phenomenon_time_range.lower.timestamp()] = observations[i].result

    (anomalyScore, anomalyPeriod) = anomaly_detect(obs_reduced)

    for i in range(len(property_values)):
        if property_values[i] is None:
            anomalyScore.insert(i, None)

    return {
        'phenomenon_time_range': phenomenon_time_range,
        'property_values': property_values,
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



