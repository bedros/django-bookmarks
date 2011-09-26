from datetime import datetime
import urllib2

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    CreateView, DateDetailView, DeleteView, ListView, TemplateView,
    UpdateView)

from bookmarks.models import Bookmark, BookmarkInstance
from bookmarks.forms import BookmarkInstanceForm, BookmarkInstanceEditForm

HTTP_ACCEPT = """\
text/xml,application/xml,application/xhtml+xml,text/html;\
q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5"""


def _template(name):
    return 'bookmarks/%s.html' % name


def _bookmarklet():
    return """\
javascript:location.href='%s?url='+encodeURIComponent(location.href)+';\
description='+encodeURIComponent(document.title)+';\
redirect=on'""" % reverse('bookmarks.views.add')


class BookmarksView(TemplateView):
    template_name = _template('bookmarks')

    def get_context_data(self, **kwargs):
        bookmarks = Bookmark.objects.all().order_by("-added")
        user = self.request.user
        if user.is_authenticated():
            user_bookmarks = Bookmark.objects \
                                     .filter(saved_instances__user=user)
        else:
            user_bookmarks = []
        return {
            "bookmarks": bookmarks,
            "user_bookmarks": user_bookmarks,
        }


class YourBookmarksView(ListView):
    context_object_name = 'bookmark_instances'
    model = BookmarkInstance
    template_name = _template('your_bookmarks')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user) \
                                 .order_by("-saved")


class BookmarkManipulationMixin(object):

    def _form_valid(self, form):
        self.should_redirect = form.should_redirect()
        redirect = super(self.__class__, self).form_valid(form)
        return redirect

    def _get_context_data(self, **kwargs):
        data = super(self.__class__, self).get_context_data(**kwargs)
        data['bookmarklet'] = _bookmarklet()
        return data

    def _get_form_kwargs(self):
        kwargs = super(self.__class__, self).get_form_kwargs()
        if self.request.method == 'POST':
            kwargs['user'] = self.request.user
        return kwargs

    def _get_success_url(self):
        if self.should_redirect:
            # redirect to bookmark URL
            return self.object.bookmark.url
        else:
            messages.success(self.request, self.user_success_msg() % {
                'description': self.object.description,
            })
            return reverse(self.success_view)


class BookmarkAddView(CreateView, BookmarkManipulationMixin):

    form_class = BookmarkInstanceForm
    success_view = 'bookmarks.views.bookmarks'
    template_name = _template('add')

    get_form_kwargs = lambda self: self._get_form_kwargs()
    get_success_url = lambda self: self._get_success_url()

    def form_valid(self, form):
        redirect = self._form_valid(form)
        bookmark = self.object.bookmark

        try:
            headers = {
                "Accept": HTTP_ACCEPT,
                "Accept-Language": "en-us,en;q=0.5",
                "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
                "Connection": "close",
                ##"User-Agent": settings.URL_VALIDATOR_USER_AGENT
                }
            req = urllib2.Request(bookmark.get_favicon_url(force=True),
                                  None, headers)
            urllib2.urlopen(req)
            has_favicon = True
        except Exception:
            has_favicon = False

        bookmark.has_favicon = has_favicon
        bookmark.favicon_checked = datetime.now()
        bookmark.save()
        return redirect

    def get_initial(self):
        initial = {}
        fields = ['url', 'description', 'redirect']
        for field in fields:
            if field in self.request.GET:
                initial[field] = self.request.GET[field].strip()
        return initial

    def user_success_msg(self):
        return _('You have saved bookmark "%(description)s"')


class BookmarkDeleteView(DeleteView):

    model = BookmarkInstance

    def get_queryset(self):
        return self.model.objects.filter(id=self.kwargs['pk'],
                                         user=self.request.user)

    def get_success_url(self):
        messages.success(self.request, _('Bookmark Deleted'))
        return self.request.GET.get('next',
                                    reverse("bookmarks.views.bookmarks"))


class BookmarkEditView(UpdateView, BookmarkManipulationMixin):

    form_class = BookmarkInstanceEditForm
    model = BookmarkInstance
    template_name = _template('edit')
    success_view = 'bookmarks.views.your_bookmarks'

    form_valid = lambda self, form: self._form_valid(form)
    get_form_kwargs = lambda self: self._get_form_kwargs()
    get_success_url = lambda self: self._get_success_url()

    def get_initial(self):
        initial = {}
        if self.request.user == self.object.user:
            fields = ['description', 'note', 'tags']
            initial = dict([(f, getattr(self.object, f)) for f in fields])
        return initial

    def user_success_msg(self):
        return _('You have finished editing bookmark "%(description)s"')

add = login_required(BookmarkAddView.as_view())
bookmarks = BookmarksView.as_view()
bookmark_detail = \
    DateDetailView.as_view(context_object_name='bookmark', date_field='added',
                           model=Bookmark,
                           template_name=_template('bookmark_detail'))
delete = login_required(BookmarkDeleteView.as_view())
edit = login_required(BookmarkEditView.as_view())
your_bookmarks = login_required(YourBookmarksView.as_view())
