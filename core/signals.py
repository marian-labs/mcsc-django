from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from events.models import Event
from news.models import NewsPost


@receiver([post_save, post_delete], sender=Event)
@receiver([post_save, post_delete], sender=NewsPost)
def clear_site_cache_on_content_change(sender, instance, **kwargs):
    cache.clear()
