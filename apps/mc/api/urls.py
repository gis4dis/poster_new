from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .views import PropertyViewSet, TimeSeriesViewSet, TopicViewSet
from .views_old import OldTimeSeriesViewSet


app_name = 'api-mc'


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'properties', PropertyViewSet, base_name='properties')
router.register(r'topics', TopicViewSet)
router.register(r'timeseries', TimeSeriesViewSet, base_name='timeseries')
router.register(r'timeseries2', OldTimeSeriesViewSet, base_name='timeseries2')
#router.register(r'timeseriesold', OldTimeSeriesViewSet, base_name='timeseriesold')


urlpatterns = [
    url(r'^', include(router.urls)),
]
