# mandatory, dictionary, at least one topic must be specified
TOPICS = {
    # common.Topic.name_id, dictionary, at least one property must be specified
    # topic represents an emergency situation, e.g. drought or floods
    'drought': {

        # dictionary of properties related to the topic
        # mandatory, at least one property must be specified
        'properties': {

            # common.Property.name_id
            'air_temperature': {

                # dictionary of observation providers of given property
                # mandatory, at least one provider must be specified
                'observation_providers': {

                    # path to Django model
                    # the model must be subclass of common.AbstractObservation
                    'apps.processing.ala.models.Observation': {

                        # mandatory, name_id of common.Process
                        'process': 'apps.common.aggregate.arithmetic_mean'
                    },
                },
            }
        },

        # mandatory, number of seconds
        'value_frequency': 3600
    },

    # ...
}