from apps.common.mixins import MonitoringView
from apps.processing.rsd.monitoring.checks import check_new_observations

class RSDMonitoringView(MonitoringView):

    def perform_check(self, context):
        result = {}
        result['import'] = check_new_observations(-3)

        if result and result['import']:
            return 200, result
        else:
            return 503, result
