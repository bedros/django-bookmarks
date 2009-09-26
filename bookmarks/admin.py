from django.contrib import admin
from bookmarks.models import Bookmark, BookmarkInstance

class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('url', 'description', 'added', 'adder',)
    prepopulated_fields = {'slug': ('description',)}

admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(BookmarkInstance)