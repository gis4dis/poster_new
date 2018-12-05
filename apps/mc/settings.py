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

                    'apps.processing.ozp.models.Observation': {
                        'process': 'measure'
                    }
                },
            },
            'precipitation': {
                'observation_providers': {
                    'apps.processing.ala.models.Observation': {
                        'process': 'apps.common.aggregate.arithmetic_mean',
                    },
                }
            },
            'pm10': {
                'observation_providers': {
                    'apps.processing.ozp.models.Observation': {
                        'process': 'measure',
                    },
                }
            },
            'stream_flow': {
                'observation_providers': {
                    'apps.processing.pmo.models.WatercourseObservation': {
                        'process': 'apps.common.aggregate.arithmetic_mean',
                    },
                }
            }
        },
        'time_series': {
            # datetime in ISO 8601, see https://en.wikipedia.org/wiki/ISO_8601
            'zero': '2017-09-19T00:00:00+01:00',
            # time interval in ISO 8601 "format with designators", see https://en.wikipedia.org/wiki/ISO_8601#Durations
            'frequency': 'PT1H',
            'range_from': 'PT0S',
            'range_to': 'PT1H',
        }
    },
    'floods': {

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
                    }#,
                    #'apps.processing.ozp.models.Observation': {
                    #    'process': 'measure'
                    #}
                },
            },

            'ground_air_temperature': {
                'observation_providers': {
                    'apps.processing.ala.models.Observation': {
                        'process': 'apps.common.aggregate.arithmetic_mean',
                    },
                }
            }
        },
        'time_series': {
            # datetime in ISO 8601, see https://en.wikipedia.org/wiki/ISO_8601
            'zero': '2017-09-19T00:00:00+01:00',
            # time interval in ISO 8601 "format with designators", see https://en.wikipedia.org/wiki/ISO_8601#Durations
            'frequency': 'PT1H',
            'range_from': 'PT0S',
            'range_to': 'PT1H',
        }
    },

    # ...
}

AGGREGATED_OBSERVATIONS = [

    # dictionary representing set of aggregated observations
    {

        # mandatory, definition of common.TimeSeries
        'time_series': {

            # datetime in ISO 8601, see https://en.wikipedia.org/wiki/ISO_8601
            'zero': '2018-09-19T00:00:00+01:00',

            # time interval in ISO 8601 "format with designators", see https://en.wikipedia.org/wiki/ISO_8601#Durations
            'frequency': 'PT1H',
            'range_from': 'PT0S',
            'range_to': 'PT1H',
        },

        # dictionary of observation providers
        # mandatory, at least one provider must be specified
        'observation_providers': {

            # path to Django model
            # the model must be subclass of common.AbstractObservation
            'apps.processing.ala.models.Observation': {

                # mandatory, name_id of common.Process
                'process': 'measure',

                # mandatory, list of name_ids of common.Property
                'observed_properties': ['precipitation', 'air_temperature',
                                        'ground_air_temperature'],
            },
        },
    },
]