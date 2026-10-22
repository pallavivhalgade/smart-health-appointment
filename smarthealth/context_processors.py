from django.conf import settings


def deployment(request):
    return {'demo_mode': settings.DEMO_MODE}
