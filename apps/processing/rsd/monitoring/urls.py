from django.conf.urls import url

from apps.processing.rsd.monitoring.views import RSDMonitoringView

app_name = 'monitoring.processing.pmo'


urlpatterns = [
    url(
        r'^$', RSDMonitoringView.as_view(), name="rsd-monitoring"
    ),
]
