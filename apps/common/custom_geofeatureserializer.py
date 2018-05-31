
from rest_framework.serializers import ListSerializer, LIST_SERIALIZER_KWARGS
from collections import OrderedDict
from django.core.exceptions import ImproperlyConfigured
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class CustomGeoFeatureModelListSerializer(ListSerializer):
    @property
    def data(self):
        return super(ListSerializer, self).data

    def to_representation(self, data):
        """
        Add GeoJSON compatible formatting to a serialized queryset list
        """
        return OrderedDict((
            ("time", "123456"),
            ("from", "123456"),
            ("to", "123456"),
            ("type", "FeatureCollection"),
            ("features", super(CustomGeoFeatureModelListSerializer, self).to_representation(data))
        ))

class CustomGeoFeatureModelSerializer(GeoFeatureModelSerializer):
    @classmethod
    def many_init(cls, *args, **kwargs):
        child_serializer = cls(*args, **kwargs)
        list_kwargs = {'child': child_serializer}
        list_kwargs.update(dict([
            (key, value) for key, value in kwargs.items()
            if key in LIST_SERIALIZER_KWARGS
        ]))
        meta = getattr(cls, 'Meta', None)
        list_serializer_class = getattr(meta, 'list_serializer_class', CustomGeoFeatureModelListSerializer)
        return list_serializer_class(*args, **list_kwargs)