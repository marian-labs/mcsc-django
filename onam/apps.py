from django.apps import AppConfig


class OnamConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'onam'
    verbose_name = 'Onam Championship'

    def ready(self):
        import onam.signals  # noqa: F401
