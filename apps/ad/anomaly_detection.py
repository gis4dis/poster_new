from datetime import datetime
from psycopg2.extras import DateTimeTZRange
import numpy as np
from luminol.anomaly_detector import AnomalyDetector
from luminol.constants import DEFAULT_BITMAP_MOD_MINIMAL_POINTS_IN_WINDOWS, DEFAULT_BITMAP_MOD_LEADING_WINDOW_SIZE_PCT, DEFAULT_BITMAP_MOD_LAGGING_WINDOW_SIZE_PCT

DEFAULT_ANOMALY_BREAKS = [80, 95]
DEFAULT_VALUE_BREAKS = [3, 10, 90, 97]

def observations_to_property_values(observations):
    return [obs.result for obs in observations]

def observations_to_date_range(observations):
    from_range = None
    to_range = None
    for obs in observations:
        if from_range is None or from_range > obs.phenomenon_time_range.lower:
            from_range = obs.phenomenon_time_range.lower

        if to_range is None or to_range < obs.phenomenon_time_range.upper:
            to_range = obs.phenomenon_time_range.upper

    if from_range and to_range:
        return DateTimeTZRange(from_range, to_range)

    return DateTimeTZRange()

def percentiles(
    values,
    breaks,
):
    vals = np.array([float(value) for value in values if value is not None])

    if vals.size == 0:
        return {}

    percentiles = np.percentile(vals, breaks)

    return {breaks[i]: float(percentiles[i]) for i in range(len(percentiles))}


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
        anomaly_breaks=DEFAULT_ANOMALY_BREAKS,
        value_breaks=DEFAULT_VALUE_BREAKS,
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
            'property_value_percentiles': {},
            'property_anomaly_rates': [],
            'property_anomaly_percentiles': {},
        }

    property_values = observations_to_property_values(observations)

    VALID_VALUES_LENGTH = len(property_values) - property_values.count(None)

    if VALID_VALUES_LENGTH == 1:
        return {
            'phenomenon_time_range': observations_to_date_range(observations), #phenomenon_time_range,
            'property_values': property_values,
            'property_value_percentiles': {50: property_values[0]},
            'property_anomaly_rates': [0],
            'property_anomaly_percentiles': {0: 0},
        }

    MINIMAL_POINTS_IN_WINDOWS = DEFAULT_BITMAP_MOD_MINIMAL_POINTS_IN_WINDOWS

    if use_baseline:
        MINIMAL_POINTS_IN_WINDOWS /= 2

    # if VALID_VALUES_LENGTH <= MINIMAL_POINTS_IN_WINDOWS:
    #     # warn the user?

    WINDOW_LENGTH = detector_params["future_window_size"] if use_baseline else detector_params["future_window_size"] + detector_params["lag_window_size"]

    if VALID_VALUES_LENGTH > MINIMAL_POINTS_IN_WINDOWS and VALID_VALUES_LENGTH <= WINDOW_LENGTH:
        detector_params["future_window_size"] = int(max(DEFAULT_BITMAP_MOD_MINIMAL_POINTS_IN_WINDOWS / 2, VALID_VALUES_LENGTH * DEFAULT_BITMAP_MOD_LEADING_WINDOW_SIZE_PCT))
        detector_params["lag_window_size"] = int(max(DEFAULT_BITMAP_MOD_MINIMAL_POINTS_IN_WINDOWS / 2, VALID_VALUES_LENGTH * DEFAULT_BITMAP_MOD_LAGGING_WINDOW_SIZE_PCT))

    property_value_percentiles = percentiles(property_values[lower_ext:lower_ext+num_time_slots], value_breaks)

    if use_baseline and baseline_time_range is None:
        baseline_time_series = observations
        baseline_reduced = {obs.phenomenon_time_range.lower.timestamp(): obs.result for obs in baseline_time_series}

    obs_reduced = {obs.phenomenon_time_range.lower.timestamp(): obs.result for obs in observations}

    if (VALID_VALUES_LENGTH <= 1):
        property_anomaly_rates = [0 if value is not None else value for value in property_values[lower_ext:lower_ext+num_time_slots]]

        return {
            'phenomenon_time_range': observations_to_date_range(observations[lower_ext:lower_ext + num_time_slots]), #, phenomenon_time_range,
            'property_values': property_values[lower_ext:lower_ext+num_time_slots],
            'property_value_percentiles': property_value_percentiles,
            'property_anomaly_rates': property_anomaly_rates,
            'property_anomaly_percentiles': {0: 0},
        }

    try:
        baseline_reduced
    except NameError:
        detector = AnomalyDetector(obs_reduced, algorithm_name=detector_method, algorithm_params=detector_params, score_only=True)
    else:
        detector = AnomalyDetector(obs_reduced, baseline_reduced, algorithm_name=detector_method, algorithm_params=detector_params, score_only=True)

    property_anomaly_rates = detector.get_all_scores().values

    property_anomaly_percentiles = percentiles(property_anomaly_rates[lower_ext:lower_ext+num_time_slots], anomaly_breaks)

    for i in range(len(property_values)):
        if property_values[i] is None:
            property_anomaly_rates.insert(i, None)

    return {
        'phenomenon_time_range': observations_to_date_range(observations[lower_ext:lower_ext+num_time_slots]), #phenomenon_time_range,
        'property_values': property_values[lower_ext:lower_ext+num_time_slots],
        'property_value_percentiles': property_value_percentiles,
        'property_anomaly_rates': property_anomaly_rates[lower_ext:lower_ext+num_time_slots],
        'property_anomaly_percentiles': property_anomaly_percentiles,
    }
