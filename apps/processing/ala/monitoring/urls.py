from django.urls import path

from apps.processing.ala.monitoring.views import AlaMonitoringView

app_name = 'monitoring.processing.ala'


urlpatterns = [
    path('', AlaMonitoringView.as_view(), name="ala-monitoring"),
]
