from django.conf.urls.defaults import *
from bookmarks.models import Bookmark

urlpatterns = patterns('',
    url(r'^$', 'bookmarks.views.bookmarks', name="all_bookmarks"),
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        view='bookmarks.views.bookmark_detail',
        name='bookmark_detail'),
    url(r'^your_bookmarks/$', 'bookmarks.views.your_bookmarks', name="your_bookmarks"),
    url(r'^add/$', 'bookmarks.views.add', name="add_bookmark"),
    url(r'^(\d+)/delete/$', 'bookmarks.views.delete', name="delete_bookmark_instance"),
)
