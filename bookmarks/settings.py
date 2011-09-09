from django.conf import settings

DEFAULT_SETTINGS = {
    'VERIFY_EXISTS': False,
}

DEFAULT_SETTINGS.update(getattr(settings, 'BOOKMARK_SETTINGS', {}))

globals().update(DEFAULT_SETTINGS)
