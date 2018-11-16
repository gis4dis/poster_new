from apps.common.mixins import MonitoringView


class PMOMonitoringView(MonitoringView):

    def perform_check(self, context):

        # return {"x": "a"}
        raise Exception("Something went wrong")
