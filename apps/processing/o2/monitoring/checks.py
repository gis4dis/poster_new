from datetime import timedelta, datetime, time
from itertools import product

from psycopg2._range import DateTimeTZRange, NumericRange

from apps.common import models as common_models
from apps.common.models import Property, Process
from apps.processing.o2.models import ANY_OCCURRENCE, OCCURRENCE_CHOICES, UNIQUES_CHOICES, MobilityObservation, \
    SocioDemoObservation, MALE_GENDER, FEMALE_GENDER
from apps.processing.o2.util import util
from apps.processing.o2.util.util import get_or_create_props, get_or_create_processes, get_or_create_common_props, \
    get_or_create_common_processes
from apps.utils.time import UTC_P0100


def check_o2_mobility():
    phenomenon_time = datetime.now()
    streams = util.get_or_create_streams()
    occurrence_types = tuple(filter(lambda occ: occ[0] != ANY_OCCURRENCE,
                                    OCCURRENCE_CHOICES))

    # 126 * 2 * 2 * 2 = 1008
    all_query_defs = list(product(streams, occurrence_types,
                                  occurrence_types, UNIQUES_CHOICES))

    def pt_to_range(phenomenon_time):
        pt_range = DateTimeTZRange(
            phenomenon_time,
            phenomenon_time + timedelta(1)
        )
        return pt_range

    pt_range = pt_to_range(phenomenon_time)

    get_or_create_props()
    observed_property = Property.objects.get(name_id='mobility')
    get_or_create_processes()
    procedure = Process.objects.get(name_id='estimation')

    def get_obs(query_def):
        try:
            obs = MobilityObservation.objects.get(
                phenomenon_time_range=pt_range,
                observed_property=observed_property,
                procedure=procedure,
                feature_of_interest=query_def[0],
                src_occurrence_type=query_def[1][0],
                dst_occurrence_type=query_def[2][0],
                uniques_type=query_def[3][0],
            )
            if obs.result_null_reason not in ("", "HTTP Error 204"):
                obs = None
        except MobilityObservation.DoesNotExist:
            obs = None
        return obs

    query_defs = list(filter(lambda qd: get_obs(qd) is None, all_query_defs))

    missing_count = len(all_query_defs) - len(query_defs)
    error_dict = {
        'all_query_defs': len(all_query_defs),
        'query_defs': len(query_defs),
        'missing_defs': missing_count,
    }
    return error_dict


def check_o2_sociodemo():
    phenomenon_date = datetime.now()
    zsjs = util.get_or_create_shopping_mall_zsjs()

    get_or_create_common_props()
    observed_property = common_models.Property.objects.get(
        name_id='population')
    get_or_create_common_processes()
    procedure = common_models.Process.objects.get(name_id='estimation')

    age_types = list(map(lambda v: str(v), range(1, 6)))

    def age_type_to_range(age_type):
        # (1: 8-18, 2: 19-25, 3: 26-35, 4: 36-55, 5: 56+)
        result = None
        if age_type == "1":
            result = NumericRange(8, 18, '[]')
        elif age_type == "2":
            result = NumericRange(19, 25, '[]')
        elif age_type == "3":
            result = NumericRange(26, 35, '[]')
        elif age_type == "4":
            result = NumericRange(36, 55, '[]')
        elif age_type == "5":
            result = NumericRange(56, None, '[)')
        return result

    # use only applicable occurrence types
    occurrence_types = tuple(filter(lambda occ: occ[0] != ANY_OCCURRENCE,
                                    OCCURRENCE_CHOICES))

    def gender_value_to_type(gender_value):
        result = None
        if gender_value == "1":
            result = MALE_GENDER
        elif gender_value == "2":
            result = FEMALE_GENDER
        return result

    gender_values = ["1", "2"]

    hours = list(map(lambda v: str(v), range(0, 24, 2)))

    age_gender_types = list(map(
        lambda age_type: {
            'url-path': 'age',
            'url-params': {
                'ageGroup': age_type
            },
            'obs-props': {
                'age': age_type_to_range(age_type),
                'gender': '-'
            }
        },
        age_types
    )) + list(map(
        lambda gender_value: {
            'url-path': 'gender',
            'url-params': {
                'g': gender_value
            },
            'obs-props': {
                'gender': gender_value_to_type(gender_value),
                'age': NumericRange(0, None, '[)')
            }
        },
        gender_values
    ))

    all_query_defs = list(product(zsjs, age_gender_types,
                                  occurrence_types, hours))

    def hour_to_pt_range(hour):
        time_from = time(int(hour))
        pt_from = datetime.combine(
            phenomenon_date.date(), time_from).replace(tzinfo=UTC_P0100)
        pt_range = DateTimeTZRange(pt_from, pt_from + timedelta(hours=1))
        return pt_range

    def get_obs(query_def):
        obs_props = {
            'phenomenon_time_range': hour_to_pt_range(query_def[3]),
            'observed_property': observed_property,
            'procedure': procedure,
            'feature_of_interest': query_def[0],
            'occurrence_type': query_def[2][0],
        }
        obs_props.update(query_def[1]['obs-props'])
        try:
            obs = SocioDemoObservation.objects.get(**obs_props)
            if obs.result_null_reason not in ("", "HTTP Error 204"):
                obs = None
        except SocioDemoObservation.DoesNotExist:
            obs = None
        return obs

    query_defs = list(filter(lambda qd: get_obs(qd) is None, all_query_defs))

    missing_count = len(all_query_defs) - len(query_defs)
    error_dict = {
        'all_query_defs': len(all_query_defs),
        'query_defs': len(query_defs),
        'missing_defs': missing_count,
    }
    return error_dict
