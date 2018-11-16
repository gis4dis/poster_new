from django.conf.urls import url

from apps.processing.pmo.monitoring.views import PMOMonitoringView

app_name = 'monitoring.processing.pmo'


urlpatterns = [
    url(
        r'^$', PMOMonitoringView.as_view(), name="pmo-monitoring"
    ),
]
