# -*- coding: utf-8 -*-
from bookmarks.models import Bookmark, BookmarkInstance
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

TEST_USERNAME = 'testuser'
TEST_PASSWORD = 'testpw'


class BookmarkViewsTestCase(TestCase):
    fixtures = ['bookmarks']
    urls = 'bookmarks.urls'

    @classmethod
    def setUpClass(cls):
        User.objects.create_user(TEST_USERNAME, 'test@example.com',
                                 TEST_PASSWORD)

    def setUp(self):
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

    def create_bookmark(self, bookmark_url, redirect=False):
        return self.client.post(reverse('add_bookmark'), {
            'url': bookmark_url,
            'description': 'Test bookmark',
            'redirect': redirect,
            'tags': 'foo,bar',
        })

    def tag_list(self, instance):
        return [t.name for t in instance.tags.all()]

    def test_add(self):
        response = self.client.get(reverse('add_bookmark'))
        self.assertEqual(200, response.status_code)

        original_bookmark_ct = Bookmark.objects.all().count()
        original_bookmark_instance_ct = BookmarkInstance.objects.all().count()
        bookmark_url = 'http://www.google.com/'
        response = self.create_bookmark(bookmark_url)
        self.assertEqual(302, response.status_code)
        self.assertNotEqual(bookmark_url, response['Location'])
        self.assertEqual(original_bookmark_ct + 1,
                         Bookmark.objects.all().count())
        self.assertEqual(original_bookmark_instance_ct + 1,
                         BookmarkInstance.objects.all().count())
        bookmark = Bookmark.objects.get(url=bookmark_url)
        instance = BookmarkInstance.objects.get(bookmark=bookmark)
        self.assertEqual(self.tag_list(instance), ['foo', 'bar'])

        bookmark_url = 'http://www.google.ca/'
        response = self.create_bookmark(bookmark_url, redirect=True)
        self.assertEqual(302, response.status_code)
        self.assertEqual(bookmark_url, response['Location'])
        self.assertEqual(original_bookmark_ct + 2,
                         Bookmark.objects.all().count())
        self.assertEqual(original_bookmark_instance_ct + 2,
                         BookmarkInstance.objects.all().count())

    def test_edit(self):
        bookmark_url = 'http://www.google.com/'
        self.create_bookmark(bookmark_url)
        bookmark = Bookmark.objects.get(url=bookmark_url)
        instance = BookmarkInstance.objects.get(bookmark=bookmark)
        tags = self.tag_list(instance)

        response = self.client.get(reverse('edit_bookmark_instance',
                                           args=[instance.id]))
        self.assertEqual(200, response.status_code)

        response = self.client.post(reverse('edit_bookmark_instance',
                                            args=[instance.id]), {
            'description': 'Test bookmark (edit)',
            'tags': 'foo,bar,baz',
        })
        self.assertEquals(302, response.status_code)
        self.assertNotEquals(bookmark_url, response['Location'])
        instance2 = BookmarkInstance.objects.get(bookmark=bookmark)
        self.assertNotEqual(instance.description, instance2.description)
        self.assertNotEqual(tags, self.tag_list(instance2))

    def test_delete(self):
        original_bookmark_ct = Bookmark.objects.all().count()
        original_bookmark_instance_ct = BookmarkInstance.objects.all().count()
        bookmark_url = 'http://www.google.com/'
        self.create_bookmark(bookmark_url)
        bookmark = Bookmark.objects.get(url=bookmark_url)
        instance = BookmarkInstance.objects.get(bookmark=bookmark)
        self.assertEqual(original_bookmark_ct + 1,
                         Bookmark.objects.all().count())
        self.assertEqual(original_bookmark_instance_ct + 1,
                         BookmarkInstance.objects.all().count())
        response = self.client.post(reverse('delete_bookmark_instance',
                                            args=[instance.id]))
        self.assertEquals(302, response.status_code)
        self.assertEqual(original_bookmark_ct,
                         Bookmark.objects.all().count())
        self.assertEqual(original_bookmark_instance_ct,
                         BookmarkInstance.objects.all().count())

        # ID that doesn't exist
        response = self.client.post(reverse('delete_bookmark_instance',
                                            args=[1000]))
        self.assertEquals(404, response.status_code)
