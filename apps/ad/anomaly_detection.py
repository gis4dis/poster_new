from datetime import datetime
from psycopg2.extras import DateTimeTZRange
from luminol.anomaly_detector import AnomalyDetector


def get_timeseries(
        phenomenon_time_range,
        property_values,
        time_series):

    if not isinstance(property_values, list):
        raise Exception('property_values should be array')

    if len(property_values) == 0:
        return {
            'phenomenon_time_range': DateTimeTZRange(),
            'value_frequency': None,
            'property_values': [],
            'property_anomaly_rates': [],
        }

    #todo Tu je mozna problem ze neznam presne observations (takze na vystup predam zase phenomenom_time_range)
    #   asi by bylo mozne k zacatku intervalu pricist frequency z timeseries
    if len(property_values) == 1:
        return {
            'phenomenon_time_range': phenomenon_time_range,
            'value_frequency': time_series.frequency,
            'property_values': property_values,
            'property_anomaly_rates': [0],
        }

    obs_reduced = {}

    for i in range(len(property_values)):
        obs_reduced[i] = property_values[i]

    (anomalyScore, anomalyPeriod) = anomaly_detect(obs_reduced)

    for i in range(len(property_values)):
        if obs_reduced[i] is None:
            anomalyScore.insert(i, None)

    return {
        'phenomenon_time_range': phenomenon_time_range,
        'value_frequency': time_series.frequency,
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



