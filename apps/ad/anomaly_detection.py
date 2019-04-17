from datetime import datetime
from psycopg2.extras import DateTimeTZRange
from luminol.anomaly_detector import AnomalyDetector


def observations_to_property_values(observations):
    return [obs.result for obs in observations]


def get_timeseries(
        phenomenon_time_range,
        num_time_slots,
        get_observations,
        detector_method='bitmap_mod',
        detector_params={
            "precision": 6,
            "lag_window_size": 96,
            "future_window_size": 96,
            "chunk_size": 2
        },
        extend_range=True,
        baseline_time_range=None,
        shift=True,
        use_baseline=True
):
    #observations = get_observations(3, 5)
    #observations = get_observations(0, 0)

    # if baseline_time_range is not None:
        # use_baseline = True
    #     baseline_time_series = observation_provider_model.objects.filter(
    #         phenomenon_time_range__contained_by=baseline_time_range,
    #         phenomenon_time_range__duration=frequency,
    #         phenomenon_time_range__matches=frequency,
    #         observed_property=observed_property,
    #         procedure=process,
    #         feature_of_interest=feature_of_interest
    #     )
    #     baseline_reduced = {obs.phenomenon_time_range.lower.timestamp(): obs.result for obs in baseline_time_series}

    lower_ext = 0
    upper_ext = 0

    if extend_range:
        lower_ext = detector_params["lag_window_size"]
        upper_ext = detector_params["future_window_size"]

        if use_baseline and shift:
            upper_ext = 0

        if use_baseline and not shift:
            lower_ext = int(upper_ext / 2)
            upper_ext -= lower_ext + 1

    observations = get_observations(lower_ext, upper_ext)

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

    if use_baseline and baseline_time_range is None:
        baseline_time_series = observations
        baseline_reduced = {obs.phenomenon_time_range.lower.timestamp(): obs.result for obs in baseline_time_series}

    obs_reduced = {obs.phenomenon_time_range.lower.timestamp(): obs.result for obs in observations}

    if (len(property_values) - property_values.count(None) <= 1):
        property_anomaly_rates = [0 if value is not None else value for value in property_values[lower_ext:lower_ext+num_time_slots]]

        return {
            'phenomenon_time_range': phenomenon_time_range,
            'property_values': property_values[lower_ext:lower_ext+num_time_slots],
            'property_anomaly_rates': property_anomaly_rates,
        }

    try:
        baseline_reduced
    except NameError:
        detector = AnomalyDetector(obs_reduced, algorithm_name=detector_method, algorithm_params=detector_params, score_only=True)
    else:
        detector = AnomalyDetector(obs_reduced, baseline_reduced, algorithm_name=detector_method, algorithm_params=detector_params, score_only=True)

    property_anomaly_rates = detector.get_all_scores().values

    for i in range(len(property_values)):
        if property_values[i] is None:
            property_anomaly_rates.insert(i, None)

    return {
        'phenomenon_time_range': phenomenon_time_range,
        'property_values': property_values[lower_ext:lower_ext+num_time_slots],
        'property_anomaly_rates': property_anomaly_rates[lower_ext:lower_ext+num_time_slots],
    }
