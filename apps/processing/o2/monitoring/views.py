from apps.common.mixins import MonitoringView
from apps.processing.o2.monitoring.checks import check_o2_mobility, check_o2_sociodemo


class O2MobilityMonitoringView(MonitoringView):
    def perform_check(self, context):
        error_dict = check_o2_mobility()

        if error_dict and error_dict.get('missing_defs', -1) != 0:
            return 503, error_dict

        return 200, error_dict


class O2SociodemoMonitoringView(MonitoringView):
    def perform_check(self, context):
        error_dict = check_o2_sociodemo()

        if error_dict and error_dict.get('missing_defs', -1) != 0:
            return 503, error_dict

        return 200, error_dict
