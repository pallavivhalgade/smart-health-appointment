from django.conf import settings
from django.shortcuts import render


class DemoModeMiddleware:
    """Keep the public demo read-only, including direct requests to account routes."""

    PUBLIC_PATHS = {'/', '/health/', '/appointments/doctors/', '/symptom-checker/'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEMO_MODE and not request.path.startswith('/static/'):
            allowed = request.path in self.PUBLIC_PATHS and request.method in ('GET', 'HEAD')
            # Anonymous checks are computed without saving input or results.
            allowed = allowed or (request.path == '/symptom-checker/' and request.method == 'POST')
            if not allowed:
                response = render(request, 'demo_notice.html', status=200 if request.method in ('GET', 'HEAD') else 405)
                if response.status_code == 405:
                    response['Allow'] = 'GET, HEAD'
                return response
        return self.get_response(request)
