from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .views import PropertyViewSet, TimeSeriesViewSet, TopicViewSet, VgiViewSet

app_name = 'api-mc'

router = DefaultRouter()
router.register(r'properties', PropertyViewSet, base_name='properties')
router.register(r'topics', TopicViewSet)
router.register(r'timeseries', TimeSeriesViewSet, base_name='timeseries')
router.register(r'vgi_observations', VgiViewSet, base_name='vgi_observations')

urlpatterns = [
    url(r'^', include(router.urls)),
]
