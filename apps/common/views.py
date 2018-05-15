from rest_framework import viewsets
from apps.common.serializers import ProcessSerializer, PropertySerializer, WatercourseStationSerializer
from apps.common.models import Process, Property
from apps.processing.pmo.models import WatercourseStation
from rest_framework.decorators import api_view
from rest_framework.response import Response


class ProcessViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer


class PropertyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer


class WaterCourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WatercourseStation.objects.all()
    serializer_class = WatercourseStationSerializer


@api_view(['GET'])
def processes_list(request):
    if request.method == 'GET':
        processes = Process.objects.all()
        serializer = ProcessSerializer(processes, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def watercourse_stations_list(request):
    if request.method == 'GET':
        stations = WatercourseStation.objects.all()
        serializer = WatercourseStationSerializer(stations, many=True)
        return Response(serializer.data)

