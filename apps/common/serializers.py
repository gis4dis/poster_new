from rest_framework import serializers
from apps.common.models import Property, TimeSeriesFeature
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ('name_id', 'name', 'unit')


class TimeSeriesFeatureSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = TimeSeriesFeature
        geo_field = "geometry"
        fields = (
            'id',
            'id_by_provider',
            'name',
            'phenomenon_time_from',
            'phenomenon_time_to',
            'property_values',
            'property_anomaly_rates'
        )


class TimeSeriesSerializer(serializers.Serializer):
    phenomenon_time_from = serializers.DateTimeField()
    phenomenon_time_to = serializers.DateTimeField()
    value_frequency = serializers.IntegerField()
    data = TimeSeriesFeatureSerializer(many=True)
