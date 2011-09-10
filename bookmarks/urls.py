from django.conf.urls.defaults import patterns, url

# for voting
from voting.views import vote_on_object
from bookmarks.models import Bookmark
from bookmarks.forms import BookmarkInstanceForm, BookmarkInstanceEditForm

DETAIL_REGEX = r'''\
^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$'''

urlpatterns = patterns('',
    url(r'^$', 'bookmarks.views.bookmarks', name="all_bookmarks"),
    url(DETAIL_REGEX, view='bookmarks.views.bookmark_detail',
        name='bookmark_detail'),
    url(r'^your_bookmarks/$', 'bookmarks.views.your_bookmarks',
        name="your_bookmarks"),
    url(r'^add/$', 'bookmarks.views.add', name="add_bookmark"),
    url(r'^(\d+)/delete/$', 'bookmarks.views.delete',
        name="delete_bookmark_instance"),
    url(r'^(\d+)/edit/$', 'bookmarks.views.edit',
        name="edit_bookmark_instance"),

    # for json
    url(r'^json/(?P<model_name>[\d\w]+)/$',
        'bookmarks.serializers.bookmarks_json'),
    url(r'^json/(?P<model_name>[\d\w]+)/(?P<object_id>\d+)/$',
        'bookmarks.serializers.bookmarks_json'),
#    (r'^json/', include('json.urls')),
    # for xml
    url(r'^xml/(?P<model_name>[\d\w]+)/$',
        'bookmarks.serializers.bookmarks_xml'),
    url(r'^xml/(?P<model_name>[\d\w]+)/(?P<object_id>\d+)/$',
        'bookmarks.serializers.bookmarks_xml'),

    # for voting
    (r'^(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$',
        vote_on_object, dict(
            model=Bookmark,
            template_object_name='bookmark',
            template_name='kb/link_confirm_vote.html',
            allow_xmlhttprequest=True)),

    # ajax validation
    (r'^validate_add/$', 'ajax_validation.views.validate',
        {'form_class': BookmarkInstanceForm,
        'callback': lambda request,
        *args,
        **kwargs: {'user': request.user}},
        'bookmark_instance_form_validate'),

    # ajax validation
    (r'^validate_edit/$', 'ajax_validation.views.validate',
        {'form_class': BookmarkInstanceEditForm,
        'callback': lambda request,
        *args,
        **kwargs: {'user': request.user}},
        'bookmark_instance_edit_form_validate'),
)
