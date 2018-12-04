from datetime import datetime
from psycopg2.extras import DateTimeTZRange

from luminol.anomaly_detector import AnomalyDetector

import apps.common.lookups

def get_timeseries(
        observed_property,
        observation_provider_model,
        feature_of_interest,
        phenomenon_time_range,
        process,
        frequency,
        detector_method='bitmap_mod',
        detector_params={
            "precision": 6,
            "lag_window_size": 96,
            "future_window_size": 96,
            "chunk_size": 2
        },
        baseline_time_range=None,
        extend_range=True):

    timezone = phenomenon_time_range.lower.tzinfo
    
    requested_tr_length = (phenomenon_time_range.upper.timestamp() - phenomenon_time_range.lower.timestamp()) / frequency

    if baseline_time_range is not None:
        baseline_time_series = observation_provider_model.objects.filter(
            phenomenon_time_range__contained_by=baseline_time_range,
            phenomenon_time_range__duration=frequency,
            phenomenon_time_range__matches=frequency,
            observed_property=observed_property,
            procedure=process,
            feature_of_interest=feature_of_interest
        )
        baseline_reduced = {obs.phenomenon_time_range.lower.timestamp(): obs.result for obs in baseline_time_series}

    query_time_range = phenomenon_time_range

    if extend_range:
        lower_ext = detector_params["lag_window_size"] * frequency
        upper_ext = detector_params["future_window_size"] * frequency

        if baseline_time_range:
            lower_ext = int(upper_ext / 2)
            upper_ext -= lower_ext + 1

        query_time_range = DateTimeTZRange(
            datetime.fromtimestamp(phenomenon_time_range.lower.timestamp() - lower_ext).replace(tzinfo=timezone),
            datetime.fromtimestamp(phenomenon_time_range.upper.timestamp() + upper_ext).replace(tzinfo=timezone)
        )

        

    obss = observation_provider_model.objects.filter(
        phenomenon_time_range__contained_by=query_time_range,
        phenomenon_time_range__duration=frequency,
        phenomenon_time_range__matches=frequency,
        observed_property=observed_property,
        procedure=process,
        feature_of_interest=feature_of_interest
    )

    obs_reduced = {obs.phenomenon_time_range.lower.timestamp(): obs.result for obs in obss}

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

    if len(obs_reduced.keys()) == 1:
        return {
            'phenomenon_time_range': DateTimeTZRange(datetime.fromtimestamp(result_time_range.lower).replace(tzinfo=timezone), datetime.fromtimestamp(result_time_range.upper + frequency).replace(tzinfo=timezone)),
            'value_frequency': frequency,
            'property_values': [list(obs_reduced.values())[0]],
            'property_anomaly_rates': [0],
        }

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
    
    if len(obs_reduced.keys()) == 1:
        return {
            'phenomenon_time_range': DateTimeTZRange(datetime.fromtimestamp(result_time_range.lower).replace(tzinfo=timezone), datetime.fromtimestamp(result_time_range.upper + frequency).replace(tzinfo=timezone)),
            'value_frequency': frequency,
            'property_values': [list(obs_reduced.values())[0]],
            'property_anomaly_rates': [0],
        }

    try:
        baseline_reduced
    except NameError:
        detector = AnomalyDetector(obs_reduced, algorithm_name=detector_method, algorithm_params=detector_params, score_only=True)
    else:
        detector = AnomalyDetector(obs_reduced, baseline_reduced, algorithm_name=detector_method, algorithm_params=detector_params, score_only=True)

    anomalyScore = detector.get_all_scores()

    dt = result_time_range.upper - result_time_range.lower

    for i in range(0, int(dt/frequency) + 1):
        t = result_time_range.lower + i * frequency
        if t not in obs_reduced or obs_reduced[t] is None:
            obs_reduced[t] = None
            anomalyScore[t] = None

    print(datetime.fromtimestamp(result_time_range.lower).replace(tzinfo=timezone))

    if datetime.fromtimestamp(result_time_range.lower).replace(tzinfo=timezone) not in phenomenon_time_range:
        while obs_reduced and obs_reduced[result_time_range.lower] is None or datetime.fromtimestamp(result_time_range.lower).replace(tzinfo=timezone) not in phenomenon_time_range:
            del obs_reduced[result_time_range.lower]
            del anomalyScore[result_time_range.lower]
            if obs_reduced:
                result_time_range = DateTimeTZRange(
                    min(list(obs_reduced.keys())),
                    result_time_range.upper
                )
    
    if datetime.fromtimestamp(result_time_range.upper).replace(tzinfo=timezone) not in phenomenon_time_range:
        while obs_reduced and obs_reduced[result_time_range.upper] is None or datetime.fromtimestamp(result_time_range.upper).replace(tzinfo=timezone) not in phenomenon_time_range:
            del obs_reduced[result_time_range.upper]
            del anomalyScore[result_time_range.upper]
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

    if len(obs_reduced.keys()) == 1:
        return {
            'phenomenon_time_range': DateTimeTZRange(datetime.fromtimestamp(result_time_range.lower).replace(tzinfo=timezone), datetime.fromtimestamp(result_time_range.upper + frequency).replace(tzinfo=timezone)),
            'value_frequency': frequency,
            'property_values': [list(obs_reduced.values())[0]],
            'property_anomaly_rates': [list(anomalyScore.values())[0]],
        }

    return {
        'phenomenon_time_range': DateTimeTZRange(datetime.fromtimestamp(result_time_range.lower).replace(tzinfo=timezone), datetime.fromtimestamp(result_time_range.upper + frequency).replace(tzinfo=timezone)),
        'value_frequency': frequency,
        'property_values': [value for (key, value) in sorted(obs_reduced.items())],
        'property_anomaly_rates': [value for (key, value) in sorted(anomalyScore.items())]
    }