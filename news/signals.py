import logging
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import NewsAttachment, NewsPost

logger = logging.getLogger(__name__)

@receiver(post_save, sender=NewsPost)
def handle_news_saved(sender, instance, **kwargs):
    if instance.poster_image and instance.poster_image.name:
        clean_name = instance.poster_image.name.replace('\\', '/')
        cache.delete(f"supabase_url:{clean_name}")

@receiver(pre_delete, sender=NewsAttachment)
def auto_delete_news_attachment_file(sender, instance, **kwargs):
    """
    Deletes attachment file from storage (Supabase S3 / local)
    when a NewsAttachment record is deleted.
    """
    if instance.file and instance.file.name:
        try:
            clean_name = instance.file.name.replace('\\', '/')
            cache.delete(f"supabase_url:{clean_name}")
            instance.file.storage.delete(clean_name)
            logger.info(f"Successfully deleted attachment '{clean_name}' from storage.")
        except Exception as e:
            logger.warning(f"Failed to delete attachment '{instance.file.name}' from storage: {e}")

@receiver(pre_delete, sender=NewsPost)
def auto_delete_news_post_attachments(sender, instance, **kwargs):
    """
    Deletes news poster image and all associated attachment files from storage
    when a parent NewsPost is deleted.
    """
    if instance.poster_image and instance.poster_image.name:
        try:
            clean_name = instance.poster_image.name.replace('\\', '/')
            cache.delete(f"supabase_url:{clean_name}")
            instance.poster_image.storage.delete(clean_name)
            logger.info(f"Successfully deleted poster '{clean_name}' from storage on NewsPost deletion.")
        except Exception as e:
            logger.warning(f"Failed to delete poster '{instance.poster_image.name}' from storage: {e}")

    for attachment in instance.attachments.all():
        if attachment.file and attachment.file.name:
            try:
                clean_name = attachment.file.name.replace('\\', '/')
                cache.delete(f"supabase_url:{clean_name}")
                attachment.file.storage.delete(clean_name)
                logger.info(f"Successfully deleted attachment '{clean_name}' from storage on NewsPost deletion.")
            except Exception as e:
                logger.warning(f"Failed to delete attachment '{attachment.file.name}' from storage: {e}")
