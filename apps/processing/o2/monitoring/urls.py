from django.urls import path

from apps.processing.o2.monitoring.views import O2MobilityMonitoringView, O2SociodemoMonitoringView

app_name = 'monitoring.processing.o2'


urlpatterns = [
    path('mobility', O2MobilityMonitoringView.as_view(), name="o2-monitoring-mobility"),
    path('sociodemo', O2SociodemoMonitoringView.as_view(), name="o2-monitoring-sociodemo"),
]
