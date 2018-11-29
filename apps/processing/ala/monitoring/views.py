from apps.common.mixins import MonitoringView
from apps.processing.ala.monitoring.checks import check_ala


class AlaMonitoringView(MonitoringView):
    def perform_check(self, context):
        error_dict = check_ala()
        if error_dict:
            return 503, error_dict
