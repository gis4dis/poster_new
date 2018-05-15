from rest_framework import serializers
from apps.common.models import Process, Property
from apps.processing.pmo.models import WatercourseStation
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ('name_id', 'name', 'unit', 'default_mean')


class ProcessSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Process
        fields = ('name_id', 'name')

#Simple json with point field
class SimpleWatercourseStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatercourseStation
        fields = ('id', 'name', 'geometry', 'watercourse')

#featurecollection
class WatercourseStationSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = WatercourseStation
        geo_field = "geometry"
        fields = ('id', 'name', 'watercourse')