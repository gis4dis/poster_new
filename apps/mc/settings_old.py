PROPERTIES = {

    # common.Property.name_id
    'air_temperature': {

        # dictionary of observation providers of given property
        # mandatory, at least one provider must be specified
        'observation_providers': {

            # path to Django model
            # the model must be subclass of common.AbstractObservation
            'apps.processing.ala.models.Observation': {

                # mandatory, name_id of common.Process
                'process': 'apps.common.aggregate.arithmetic_mean',
            },
        },

        # mandatory, number of seconds
        'value_frequency': 3600,
    },

    'water_level': {
        'observation_providers': {
            'apps.processing.pmo.models.WatercourseObservation': {
                'process': 'apps.common.aggregate.arithmetic_mean',
            },
        },
        'value_frequency': 3600,
    },

    'ground_air_temperature': {
        'observation_providers': {
            'apps.processing.ala.models.Observation': {
                'process': 'apps.common.aggregate.arithmetic_mean',
            },
        },
        'value_frequency': 3600,
    },

    'stream_flow': {
        'observation_providers': {
            'apps.processing.pmo.models.WatercourseObservation': {
                'process': 'apps.common.aggregate.arithmetic_mean',
            },
        },
        'value_frequency': 3600,
    }

}
