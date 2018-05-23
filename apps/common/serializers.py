from rest_framework import serializers
from apps.common.models import Property


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ('name_id', 'name', 'unit')

