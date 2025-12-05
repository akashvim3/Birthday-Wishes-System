from django.apps import AppConfig


class WishesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wishes'
    verbose_name = 'Birthday Wishes'

    def ready(self):
        """Import signal handlers when the app is ready"""
        import wishes.signals  # noqa
