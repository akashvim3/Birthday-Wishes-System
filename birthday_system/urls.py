from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

from wishes.sitemap import StaticViewSitemap, PublicWishesSitemap, GiftSuggestionSitemap
from wishes.health import health_check

sitemaps = {
    'static': StaticViewSitemap,
    'wishes': PublicWishesSitemap,
    'gifts': GiftSuggestionSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('wishes.urls')),

    # API endpoints
    path('api/v1/', include('wishes.api.urls')),

    # Health check
    path('health/', health_check, name='health_check'),

    # Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # Robots.txt
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Debug toolbar
    import debug_toolbar

    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]