from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico', permanent=True)),
    path('sw.js', TemplateView.as_view(template_name='sw.js', content_type='application/javascript'), name='sw.js'),
    path('', include('core.urls')),
    path('representatives/', include('representatives.urls')),
    path('news/', include('news.urls')),
    path('events/', include('events.urls')),
    path('grievances/', include('grievances.urls')),
    path('accounts/', include('accounts.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),
]

# Serve media files for uploaded images & attachments when local file storage is used
if not getattr(settings, 'USE_SUPABASE_STORAGE', False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
