from apps.common.mixins import MonitoringView
from apps.processing.ala.monitoring.checks import check_ala


class AlaMonitoringView(MonitoringView):
    def perform_check(self, context):
        response_dict = check_ala()
        if response_dict and response_dict['measured-today-3'] and response_dict["aggregated-today-3"]:
            return 200, response_dict
        else:
            return 503, response_dict
