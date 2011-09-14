from django.conf.urls.defaults import include, patterns
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^bookmarks/', include('bookmarks.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('django.contrib.auth.urls')),
)

urlpatterns = (urlpatterns + patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
    )) if settings.DEBUG else urlpatterns
