import logging
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import Event

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Event)
def handle_event_saved(sender, instance, **kwargs):
    if instance.poster_image and instance.poster_image.name:
        clean_name = instance.poster_image.name.replace('\\', '/')
        cache.delete(f"supabase_url:{clean_name}")

@receiver(pre_delete, sender=Event)
def auto_delete_event_poster_file(sender, instance, **kwargs):
    """
    Deletes event poster image from storage (Supabase S3 / local)
    when an Event record is deleted.
    """
    if instance.poster_image and instance.poster_image.name:
        try:
            clean_name = instance.poster_image.name.replace('\\', '/')
            cache.delete(f"supabase_url:{clean_name}")
            instance.poster_image.storage.delete(clean_name)
            logger.info(f"Successfully deleted event poster '{clean_name}' from storage.")
        except Exception as e:
            logger.warning(f"Failed to delete event poster '{instance.poster_image.name}' from storage: {e}")
