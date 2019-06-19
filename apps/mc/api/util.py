from functools import partial
from django.conf import settings
from datetime import timedelta
from importlib import import_module
from django.db.models import F, Func, Q, Max, Min
from psycopg2.extras import DateTimeTZRange

from apps.common.models import Property, Topic, TimeSlots, Process
from apps.common.util.util import generate_intervals, generate_n_intervals


def get_empty_slots(t, pt_range_z):
    return generate_intervals(
        timeslots=t,
        from_datetime=pt_range_z.lower,
        to_datetime=pt_range_z.upper,
    )


def prepare_data(
    time_slots,
    observed_property,
    observation_provider_model,
    feature_of_interest,
    process
):
    obss = observation_provider_model.objects.filter(
        observed_property=observed_property,
        procedure=process,
        feature_of_interest=feature_of_interest,
        phenomenon_time_range__in=time_slots
    )

    obs_reduced = {obs.phenomenon_time_range.lower.timestamp(): obs for obs in obss}
    observations = []

    for i in range(0, len(time_slots)):
        slot = time_slots[i]
        st = slot.lower.timestamp()
        obs = None

        if st in obs_reduced and obs_reduced[st] and obs_reduced[st].result is not None:
            obs = obs_reduced[st]

        if obs is None:
            obs = observation_provider_model(
                phenomenon_time_range=slot,
                observed_property=observed_property,
                feature_of_interest=feature_of_interest,
                procedure=process,
                result=None
            )
        observations.append(obs)
    return observations


def get_observations(
    time_slots,
    observed_property,
    observation_provider_model,
    feature_of_interest,
    process,
    t,
    lag_window_size,
    future_window_size
):
    before_intervals = []
    after_intervals = []

    from_date =  time_slots[0].lower
    ts = generate_n_intervals(t, from_date, 3)
    time_slot_diff = ts[1].lower - ts[0].lower

    if lag_window_size and lag_window_size > 0:
        bef_time_diff = time_slot_diff * lag_window_size + \
                      (time_slots[0].upper - time_slots[0].lower)
        bef_time_diff = bef_time_diff.total_seconds()

        from_datetime = time_slots[0].lower - timedelta(seconds=bef_time_diff)

        before_intervals = generate_intervals(
            timeslots=t,
            from_datetime=from_datetime,
            to_datetime=time_slots[0].lower,
        )

        before_intervals = before_intervals[-lag_window_size:]

    if future_window_size and future_window_size > 0:
        after_time_diff = time_slot_diff * future_window_size + \
                        (time_slots[0].upper - time_slots[0].lower)
        after_time_diff = after_time_diff.total_seconds()

        to_datetime = time_slots[-1].lower + timedelta(seconds=after_time_diff)

        after_intervals = generate_intervals(
            timeslots=t,
            from_datetime=time_slots[-1].lower,
            to_datetime=to_datetime,
        )

        after_intervals = after_intervals[1:]
        after_intervals = after_intervals[-future_window_size:]

    extended_time_slots =  before_intervals + time_slots + after_intervals

    return prepare_data(
        extended_time_slots,
        observed_property,
        observation_provider_model,
        feature_of_interest,
        process
    )



def import_models(path):
    provider_module = None
    provider_model = None
    error_message = None
    try:
        path = path.rsplit('.', 1)
        provider_module = import_module(path[0])
        provider_model = getattr(provider_module, path[1])
        return provider_model, provider_module, error_message
    except ModuleNotFoundError as e:
        error_message = 'module not found'
        return provider_model, provider_module, error_message
    except AttributeError as e:
        error_message = 'function not found'
        return provider_model, provider_module, error_message


def get_topics():
    topics = settings.APPLICATION_MC.TOPICS.keys()
    return Topic.objects.filter(name_id__in=list(topics))


def get_property(topic):
    topic_param = topic.name_id
    topic = settings.APPLICATION_MC.TOPICS.get(topic_param)
    prop_names = list(topic['properties'].keys())
    queryset = Property.objects.filter(name_id__in=prop_names)
    return queryset


#TODO dodelat vstupni parametry
def get_time_slots(topic, property):
    queryset = TimeSlots.objects.all()
    return queryset


def get_observation_model_name(feature_of_interest):
    obs_model = feature_of_interest._meta.get_fields()[0].remote_field.model

    op_name = obs_model.__module__
    if op_name is None or op_name == str.__class__.__module__:
        op_name = obs_model.__class__.__name__
    else:
        op_name = op_name + '.' + obs_model.__name__

    return op_name


def get_features_of_interest(topic, properties, geom_bbox=None):
    topic = topic.name_id
    topic_config = settings.APPLICATION_MC.TOPICS.get(topic)
    out_features = []

    if not topic_config or not Topic.objects.filter(name_id=topic).exists():
        raise Exception('Topic not found.')

    model_props = {}

    properties_config = topic_config['properties']

    if topic_config:
        for prop in properties:
            prop_config = properties_config.get(prop.name_id)
            op = prop_config['observation_providers']

            for provider in op:
                if provider in model_props:
                    model_props[provider].append(prop.name_id)
                else:
                    model_props[provider] = [prop.name_id]

    for model in model_props:
        provider_module, provider_model, error_message = import_models(model)
        if error_message:
            raise Exception("Importing error - %s : %s" % (model, error_message))

        path = model.rsplit('.', 1)
        provider_module = import_module(path[0])
        provider_model = getattr(provider_module, path[1])

        feature_of_interest_model = provider_model._meta.get_field(
            'feature_of_interest').remote_field.model

        if geom_bbox:
            all_features = feature_of_interest_model.objects.filter(geometry__intersects=geom_bbox)
            out_features.extend(all_features)
        else:
            all_features = feature_of_interest_model.objects.all()
            out_features.extend(all_features)

        return out_features


def get_aggregating_process(topic, property, feature_of_interest):
    topic = topic.name_id
    topic_config = settings.APPLICATION_MC.TOPICS.get(topic)
    op_name = get_observation_model_name(feature_of_interest)
    prop_config = topic_config['properties'].get(property.name_id)['observation_providers'].get(
        op_name)
    return Process.objects.get(name_id = prop_config['process'])


def get_observation_getter(topic, property, time_slots, feature_of_interest, phenomenon_time_range):
    path = get_observation_model_name(feature_of_interest).rsplit('.', 1)
    provider_module = import_module(path[0])
    provider_model = getattr(provider_module, path[1])

    process = get_aggregating_process(topic, property, feature_of_interest)

    q_objects = Q()

    q_objects.add(Q(
        observed_property=property,
        feature_of_interest=feature_of_interest,
        procedure=process,
        time_slots=time_slots
    ), Q.OR)

    q_objects.add(Q(
        phenomenon_time_range__overlap=phenomenon_time_range
    ), Q.AND)

    pm = provider_model.objects.filter(
        q_objects
    ).values(
        'feature_of_interest',
        'procedure',
        'observed_property',
    ).annotate(
        min_b=Min(Func(F('phenomenon_time_range'), function='LOWER')),
        max_b=Max(Func(F('phenomenon_time_range'), function='UPPER'))
    ).order_by('feature_of_interest')

    if len(pm) > 0:
        data_range = DateTimeTZRange(
            pm[0]['min_b'],
            pm[0]['max_b']
        )

        feature_time_slots = get_empty_slots(time_slots, data_range)

        get_observations_func = partial(
            get_observations,
            feature_time_slots,
            property,
            provider_model,
            feature_of_interest,
            process,
            time_slots)

        return get_observations_func
    else:
        return Exception('no data')

