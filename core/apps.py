from django.apps import AppConfig
import sys
import logging


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        import core.signals
        from django.conf import settings

        if settings.DEBUG:
            is_runserver = any('manage.py' in arg for arg in sys.argv) and 'runserver' in sys.argv
            if not is_runserver:
                logger = logging.getLogger('django')
                msg = (
                    "CRITICAL WARNING: DEBUG=True is enabled in a non-runserver (WSGI/Gunicorn) context! "
                    "This causes severe memory and database performance overhead (logging connection queries) "
                    "and presents security risks. Ensure DEBUG=False is set in production .env!"
                )
                logger.warning(msg)
                print(f"\n\033[91m[MCSC PRODUCTION WARNING] {msg}\033[0m\n", file=sys.stderr)
