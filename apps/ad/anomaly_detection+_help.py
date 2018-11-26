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
        time_series):

    #timezone = phenomenon_time_range.lower.tzinfo
    timezone = time_series.zero.tzinfo

    '''
    Vyfiltrovani observaci z DB
    '''
    obss = observation_provider_model.objects.filter(
        phenomenon_time_range__contained_by=phenomenon_time_range,
        phenomenon_time_range__duration=frequency,
        phenomenon_time_range__matches=frequency,
        observed_property=observed_property,
        procedure=process,
        feature_of_interest=feature_of_interest
    )



    '''
    Z sql observations reprezentace preklopeni do objektu, kde klice jsou stringy se zacatkem intervalu
    '''
    obs_reduced = {obs.phenomenon_time_range.lower.timestamp(): obs.result for obs in obss}



    '''
    defaultni navrat pokud nejsou zadna data zadana
    '''
    if len(obs_reduced.keys()) == 0:
        return {
            'phenomenon_time_range': DateTimeTZRange(),
            'value_frequency': None,
            'property_values': [],
            'property_anomaly_rates': [],
        }



    '''
    range kde min je lower hodnota prvniho mereni a max je lower hodnota posledniho mereni
    '''
    result_time_range = DateTimeTZRange(
        min(list(obs_reduced.keys())),
        max(list(obs_reduced.keys()))
    )


    '''
    defaultni navrat pokud je jenom jedno mereni
    '''
    if len(obs_reduced.keys()) == 1:
        return {
            'phenomenon_time_range': DateTimeTZRange(datetime.fromtimestamp(result_time_range.lower).replace(tzinfo=timezone), datetime.fromtimestamp(result_time_range.upper + frequency).replace(tzinfo=timezone)),
            'value_frequency': frequency,
            'property_values': [list(obs_reduced.values())[0]],
            'property_anomaly_rates': [0],
        }


    '''
    pokud prvni mereni v obss (klic je hodnota range min) je null, tak ho odstranit nastavit
    novou hodnotu min v range (dalsi mereni podle casu)
    '''
    while obs_reduced and obs_reduced[result_time_range.lower] is None:
        del obs_reduced[result_time_range.lower]
        if obs_reduced:
            result_time_range = DateTimeTZRange(
                min(list(obs_reduced.keys())),
                result_time_range.upper
            )

    ''' stejne akorat pro posledni mereni - tedy cilem je aby zacatek i konec mel skutecnou hodnotu v db a ne null '''
    while obs_reduced and obs_reduced[result_time_range.upper] is None:
        del obs_reduced[result_time_range.upper]
        if obs_reduced:
            result_time_range = DateTimeTZRange(
                result_time_range.lower,
                max(list(obs_reduced.keys()))
            )

    #zase defaultni hodnota
    if len(obs_reduced.keys()) == 0:
        return {
            'phenomenon_time_range': DateTimeTZRange(),
            'value_frequency': None,
            'property_values': [],
            'property_anomaly_rates': [],
        }

    #zase defaultni hodnota
    if len(obs_reduced.keys()) == 1:
        return {
            'phenomenon_time_range': DateTimeTZRange(datetime.fromtimestamp(result_time_range.lower).replace(tzinfo=timezone), datetime.fromtimestamp(result_time_range.upper + frequency).replace(tzinfo=timezone)),
            'value_frequency': frequency,
            'property_values': [list(obs_reduced.values())[0]],
            'property_anomaly_rates': [0],
        }

    '''
    vypocet anomalii - vraci pole anomalii + velikost periody prvniho mereni (zacatek, konec prvniho)
    '''
    (anomalyScore, anomalyPeriod) = anomaly_detect(obs_reduced)

    '''
    doba trvani
    '''
    dt = result_time_range.upper - result_time_range.lower

    property_values = []

    '''
    cyklus, ktery iteruje po merenich - kde N je pocet intervalu ziskany jako dt/frequency,
    - cilem cyklu je prevest seznam mereni z dict na pole a pokud mereni v case "t" neexistuje
    ,tak ho dat na None a stejne tak doplnit i do anomaly pole
    '''
    for i in range(0, int(dt/frequency) + 1):
        t = result_time_range.lower + i * frequency
        if t not in obs_reduced or obs_reduced[t] is None:
            obs_reduced[t] = None
            anomalyScore.insert(i, None)
        property_values.insert(i, obs_reduced[t])


    ''' 
    zvazit jak pracova s timezone - jestli ji tam nejak poslat uz z API
    '''
    return {
        'phenomenon_time_range': DateTimeTZRange(datetime.fromtimestamp(result_time_range.lower).replace(tzinfo=timezone), datetime.fromtimestamp(result_time_range.upper + frequency).replace(tzinfo=timezone)),
        'value_frequency': frequency,
        'property_values': property_values,
        'property_anomaly_rates': anomalyScore,
    }


'''

    get_time_window(): returns a tuple (start_timestamp, end_timestamp).
    get_anomalies(): return a list of Anomaly objects.

'''

def anomaly_detect(observations, detector_method='bitmap_detector'):
    time_period = None

    my_detector = AnomalyDetector(observations, algorithm_name=detector_method)
    anomalies = my_detector.get_anomalies()

    if anomalies:
        time_period = anomalies[0].get_time_window()

    #TODO: the anomaly point

    score = my_detector.get_all_scores()

    return (list(score.itervalues()), time_period)



