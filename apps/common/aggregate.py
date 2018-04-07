from decimal import Decimal
from math import atan, sin, cos, radians, degrees
from importlib import import_module


def aggregate(prop, values):
    try:
        path = prop.default_mean.rsplit('.', 1)
        agg_function_name = path[1]
        agg_module_name = path[0]
        agg_module = import_module(agg_module_name)
        result = getattr(agg_module, agg_function_name)(values)
        result_null_reason = ''
        return result, result_null_reason
    except ModuleNotFoundError as e:
        result = None
        result_null_reason = 'aggregation module not found'
        return result, result_null_reason
    except AttributeError as e:
        result = None
        result_null_reason = 'aggregation function not found'
        return result, result_null_reason


def arithmetic_mean(values):
    return sum(values) / Decimal(len(values))


def circle_mean(values):
    count = 0
    s_sum = 0
    c_sum = 0

    for value in values:
        count += 1
        s_sum += sin(radians(value))
        c_sum += cos(radians(value))
    #Prevents ZeroDivisionError: float division by zero
    if c_sum == 0:
        c_sum = 0.0000000001
    result = degrees(atan((s_sum / count) / (c_sum / count)))

    if s_sum > 0 and c_sum > 0:
        return result
    elif c_sum < 0:
        return result + 180
    else:
        return result + 360
