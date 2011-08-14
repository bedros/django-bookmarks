from datetime import datetime

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import linebreaks, escape
from django.utils.feedgenerator import Atom1Feed

from settings import ITEMS_PER_FEED, USE_TAGGING
from models import Bookmark, BookmarkInstance


class BookmarkFeed(Feed):
    def title(self):
        return 'Bookmarks from %s' % Site.objects.get_current().domain
    def description(self):
        return "Latest bookmarks from %s" % Site.objects.get_current().domain    
    
    def link(self):
        absolute_url = reverse('rss_all_bookmarks')
        return "http://%s%s" % (
                Site.objects.get_current().domain,
                absolute_url,
            )
    
    def items(self):
        return Bookmark.objects.order_by("-added")[:ITEMS_PER_FEED]
    
    def item_title(self, bookmark):
        return bookmark.description
    
    def item_description(self, bookmark):
        return linebreaks(escape(bookmark.note))
    
    def item_author_name(self, bookmark):
        return bookmark.adder.get_full_name() or bookmark.adder.username
    
    def item_author_email(self, bookmark):
        return bookmark.adder.email
    
    def item_pubdate(self, bookmark):
        return bookmark.added
    
    def item_categories(self, bookmark):
        if USE_TAGGING:
            from tagging.models import Tag
            return bookmark.all_tags()
        else:
            return bookmark.tags.split(',')

class UserBookmarkFeed(BookmarkFeed):
    """
    Bookmark feed for a specific user
    """
    def get_object(self, request, username, *args, **kwargs):
        return get_object_or_404(User, username=username)
    
    def title(self, obj):
        return "Bookmarks saved by %s" % (obj.get_full_name() or obj.username)
    
    def description(self, obj):
        return "Latest bookmarks saved by %s" % (obj.get_full_name() or obj.username)
    
    def link(self, obj):
        absolute_url = reverse('rss_user_bookmarks', kwargs={'username':obj.username})
        return "http://%s%s" % (
                Site.objects.get_current().domain,
                absolute_url,
            )
    
    def items(self, obj):
        return BookmarkInstance.objects.filter(user=obj).order_by("-saved")[:ITEMS_PER_FEED]
    
    def author_name(self, obj):
        return obj.get_full_name() or obj.username
    
    def author_email(self, obj):
        return obj.email
    
    def item_pubdate(self, bookmark):
        return bookmark.saved
    

class AtomBookmarkFeed(BookmarkFeed):
    feed_type = Atom1Feed
    subtitle = BookmarkFeed.description
    
    def feed_guid(self):
        return self.link()

class AtomUserBookmarkFeed(UserBookmarkFeed):
    feed_type = Atom1Feed
    subtitle = UserBookmarkFeed.description
    
    def feed_guid(self, obj):
        return self.link(obj)
    
    