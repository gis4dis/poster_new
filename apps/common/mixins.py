import base64

from django.contrib.auth import authenticate
from django.http import JsonResponse, HttpResponse
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
            check = self.perform_check(context)
            if not check:
                data = {}
            else:
                status, data = check
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
        return 200, context


# noinspection PyUnresolvedReferences
class BasicAuthMonitoringMixin(object):

    def dispatch(self, request, *args, **kwargs):
        user = None

        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2:
                # NOTE: Support for only basic authentication
                if auth[0].lower() == "basic":
                    username, password = base64.b64decode(auth[1]).decode('utf-8').split(':')
                    user = authenticate(username=username, password=password)
        else:
            user = request.user

        if user is not None and user.is_active and \
                (user.is_superuser or user.groups.filter(name='monitoring').exists()):
            request.user = user
            return super(BasicAuthMonitoringMixin, self).dispatch(
                request, *args, **kwargs
            )
        return HttpResponse('Unauthorized', status=401)


class MonitoringView(BasicAuthMonitoringMixin, JSONResponseMixin, TemplateView):
    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)
