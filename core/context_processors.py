from django.conf import settings

def portal_settings(request):
    return {
        'PYQ_PORTAL_URL': getattr(settings, 'PYQ_PORTAL_URL', ''),
    }
