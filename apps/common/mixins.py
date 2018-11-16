from django.http import JsonResponse
from django.views.generic import TemplateView


class JSONResponseMixin:
    """
    A mixin that can be used to render a JSON response.
    """

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        data = {}
        status = 200

        try:
            data = self.perform_check(context)
        except Exception as e:
            data = {"error": str(e)}
            status = 503
        finally:
            return JsonResponse(
                data,
                status=status,
                **response_kwargs
            )

    def perform_check(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context


class MonitoringView(JSONResponseMixin, TemplateView):
    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)
