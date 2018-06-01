
from rest_framework import viewsets
from django.conf import settings

from apps.common.serializers import PropertySerializer
from apps.common.models import Property


class PropertyViewSet(viewsets.ReadOnlyModelViewSet):
    prop_names = settings.APPLICATION_MC.PROPERTIES.keys()
    queryset = Property.objects.filter(name_id__in=prop_names)
    serializer_class = PropertySerializer
