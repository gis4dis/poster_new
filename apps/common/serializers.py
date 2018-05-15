from rest_framework import serializers
from apps.common.models import Process, Property

class PropertySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Property
        fields = ('name_id', 'name', 'unit', 'default_mean')

class ProcessSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Process
        fields = ('name_id', 'name')
