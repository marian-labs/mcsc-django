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

# Serve media files for uploaded images & attachments
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if (settings.BASE_DIR / 'static').exists():
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')

# Custom error handlers — Django picks these up automatically
handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'

