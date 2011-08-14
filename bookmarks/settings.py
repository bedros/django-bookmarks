from django.conf import BOOKMARK_VERIFY_EXISTS

DEFAULT_SETTINGS = {
    'VERIFY_EXISTS': False,
    'USE_TAGGING': False
}

DEFAULT_SETTINGS.update(getattr(settings, 'BOOKMARK_SETTINGS', {}))

globals().update(DEFAULT_SETTINGS)