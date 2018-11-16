from apps.common.mixins import MonitoringView
from apps.processing.pmo.monitoring.checks import check_ftp_uploads


class PMOMonitoringView(MonitoringView):

    def perform_check(self, context):
        error_dict = check_ftp_uploads()
        if error_dict:
            return 503, error_dict
