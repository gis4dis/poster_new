PROPERTIES = {

    # common.Property.name_id
    'air_temperature': {

        # dictionary of observation providers of given property
        # mandatory, at least one provider must be specified
        'observation_providers': {

            # path to Django model
            # the model must be subclass of common.AbstractObservation
            'apps.processing.ala.models.Observation': {

                # currently empty, will be used later for optional filter
            },
        },

        # mandatory, number of seconds
        'value_frequency': 3600,

        # mandatory, name_id of common.Process
        'process': 'avg_hour',
    },

    'ground_air_temperature': {
        'observation_providers': {
            'apps.processing.ala.models.Observation': {},
        },
        'value_frequency': 3600,
        'process': 'avg_hour',
    },

}