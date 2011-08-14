from django.conf import settings

DEFAULT_SETTINGS = {
    'VERIFY_EXISTS': False,
    'ITEMS_PER_FEED': 20,
    'ABSOLUTE_URL_IS_BOOKMARK': True,
}

DEFAULT_SETTINGS.update(getattr(settings, 'BOOKMARK_SETTINGS', {}))

globals().update(DEFAULT_SETTINGS)
