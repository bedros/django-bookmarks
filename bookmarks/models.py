"""
A Bookmark is unique to a URL whereas a BookmarkInstance represents a
particular Bookmark saved by a particular person.

This not only enables more than one user to save the same URL as a
bookmark but allows for per-user tagging.
"""

# at the moment Bookmark has some fields that are determined by the
# first person to add the bookmark (the adder) but later we may add
# some notion of voting for the best description and note from
# amongst those in the instances.


from datetime import datetime
import urlparse

from django.db.models import permalink
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

from taggit.managers import TaggableManager

from settings import VERIFY_EXISTS, ABSOLUTE_URL_IS_BOOKMARK


class Bookmark(models.Model):

    # URL is set to false per dc-special ticket #14
    url = models.URLField(verify_exists=VERIFY_EXISTS, unique=True)
    description = models.CharField(_('description'), max_length=100)
    slug = models.SlugField()
    note = models.TextField(_('note'), blank=True)

    has_favicon = models.BooleanField(_('has favicon'))
    favicon_checked = models.DateTimeField(_('favicon checked'),
                                           default=datetime.now)

    adder = models.ForeignKey(User, blank=True, null=True,
                    related_name="added_bookmarks", verbose_name=_('adder'))
    added = models.DateTimeField(_('added'), default=datetime.now)

    tags = TaggableManager()

    def get_favicon_url(self, force=False):
        """
        return the URL of the favicon (if it exists) for the site this
        bookmark is on other return None.

        If force=True, the URL will be calculated even if it doesn't
        exist.
        """
        if self.has_favicon or force:
            base_url = '%s://%s' % urlparse.urlsplit(self.url)[:2]
            favicon_url = urlparse.urljoin(base_url, 'favicon.ico')
            return favicon_url
        return None

    def __unicode__(self):
        return self.url

    if ABSOLUTE_URL_IS_BOOKMARK:

        def get_absolute_url_not_permalinked(self):
            return self.url
        get_absolute_url = get_absolute_url_not_permalinked
    else:

        @permalink
        def get_absolute_url_permalinked(self):
            return ('bookmark_detail', None, {
                'year': self.added.year,
                'month': self.added.strftime('%b').lower(),
                'day': self.added.day,
                'slug': self.slug,
            })
        get_absolute_url = get_absolute_url_permalinked

    class Meta:
        ordering = ('-added', )


class BookmarkInstance(models.Model):

    bookmark = models.ForeignKey(Bookmark, related_name="saved_instances",
                                 verbose_name=_('bookmark'))
    user = models.ForeignKey(User, related_name="saved_bookmarks",
                             verbose_name=_('user'))
    saved = models.DateTimeField(_('saved'), default=datetime.now)

    description = models.CharField(_('description'), max_length=100)
    note = models.TextField(_('note'), blank=True)

    tags = TaggableManager()

    def save(self, force_insert=False, force_update=False, edit=False):
        if edit:
            force_update = True
        super(BookmarkInstance, self).save(force_insert, force_update)

    def delete(self):
        bookmark = self.bookmark
        super(BookmarkInstance, self).delete()
        if bookmark.saved_instances.all().count() == 0:
            bookmark.delete()

    def __unicode__(self):
        return _("%(bookmark)s for %(user)s") % {
            'bookmark': self.bookmark,
            'user': self.user,
        }

    class Meta:
        permissions = (
            ('view_bookmark', 'View a private bookmark'),
        )
