from rest_framework import viewsets
from apps.common.serializers import ProcessSerializer, PropertySerializer
from apps.common.models import Process, Property


class ProcessViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer

class PropertyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer



from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def processes_list(request):
    if request.method == 'GET':
        processes = Process.objects.all()
        serializer = ProcessSerializer(processes, many=True)
        return Response(serializer.data)

