from apps.common.mixins import MonitoringView
from apps.processing.pmo.monitoring.checks_download import check_downloads
from apps.processing.pmo.monitoring.checks_import import check_pmo


class PMOMonitoringView(MonitoringView):

    def perform_check(self, context):
        #error_dict = check_ftp_uploads()
        result = {}
        result['download'] = check_downloads()
        result['import'] = check_pmo()
        if result and result['download'] and result['download']['downloaded_files-1']:
            return 200, result
        else:
            return 503, result
