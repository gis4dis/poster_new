from rest_framework import serializers
from apps.common.models import Property
from apps.mc.models import TimeSeriesFeature
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ('name_id', 'name', 'unit')


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ('name_id', 'name')


class TimeSeriesFeatureSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = TimeSeriesFeature
        geo_field = "geometry"
        id_field = "id"
        fields = (
            'id',
            'id_by_provider',
            'name',
            'value_index_shift',
            'property_values',
            'property_anomaly_rates'
        )


class TimeSeriesSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    phenomenon_time_from = serializers.DateTimeField()
    phenomenon_time_to = serializers.DateTimeField()
    value_frequency = serializers.IntegerField()
    feature_collection = TimeSeriesFeatureSerializer(many=True)
