from django import forms
from django.utils.translation import ugettext_lazy as _

from bookmarks.models import BookmarkInstance

from settings import VERIFY_EXISTS


class BookmarkInstanceForm(forms.ModelForm):

    url = forms.URLField(label="URL", verify_exists=VERIFY_EXISTS,
                         widget=forms.TextInput(attrs={"size": 40}))
    description = forms.CharField(max_length=100,
                                  widget=forms.TextInput(attrs={"size": 40}))
    redirect = forms.BooleanField(label="Redirect", required=False)

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(BookmarkInstanceForm, self).__init__(*args, **kwargs)
        # hack to order fields
        self.fields.keyOrder = ['url', 'description', 'note', 'tags',
                                'redirect']

    def clean(self):
        if 'url' not in self.cleaned_data:
            return
        url = self.cleaned_data['url']
        url_count = BookmarkInstance.objects \
                                    .filter(bookmark__url=url,
                                            user=self.user) \
                                    .count()
        if url_count > 0:
            msg = _("You have already bookmarked this link.")
            raise forms.ValidationError(msg)
        return self.cleaned_data

    def should_redirect(self):
        return bool(self.cleaned_data["redirect"])

    def save(self, commit=True):
        self.instance.url = self.cleaned_data['url']
        return super(BookmarkInstanceForm, self).save(commit)

    class Meta:
        model = BookmarkInstance
        #fields = ('url', 'description', 'note', 'redirect')


class BookmarkInstanceEditForm(forms.ModelForm):

    description = forms.CharField(max_length=100,
                                  widget=forms.TextInput(attrs={"size": 40}))
    redirect = forms.BooleanField(label="Redirect", required=False)

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(BookmarkInstanceEditForm, self).__init__(*args, **kwargs)
        # hack to order fields
        self.fields.keyOrder = ['description', 'note', 'tags', 'redirect']

    def should_redirect(self):
        return bool(self.cleaned_data["redirect"])

    class Meta:
        model = BookmarkInstance
        #fields = ('description', 'note', 'redirect')

    def clean(self):
        # The Bookmark Instance doesn't have a url field, as we can't
        # change it.
        return self.cleaned_data
