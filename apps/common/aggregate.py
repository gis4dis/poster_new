from decimal import Decimal
from math import atan, sin, cos, radians, degrees


def avg(values):
    return sum(values) / Decimal(len(values))


def circle_mean(values):
    count = 0
    s_sum = 0
    c_sum = 0

    for value in values:
        count += 1
        s_sum += sin(radians(value))
        c_sum += cos(radians(value))
    #hack - Prevents ZeroDivisionError: float division by zero
    if c_sum == 0:
        c_sum = 0.0000000001
    result = degrees(atan((s_sum / count) / (c_sum / count)))

    '''
    try:
        result = degrees(atan((s_sum / count) / (c_sum / count)))
    except ZeroDivisionError as e:
        return 'ZeroDivisionError'
    '''

    if s_sum > 0 and c_sum > 0:
        return result
    elif c_sum < 0:
        return result + 180
    else:
        return result + 360
