from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import PermissionDenied
from .models import Grievance, GrievanceReply
from core.email import send_reply_notification, send_status_update


def get_protected_admins():
    return getattr(settings, 'PROTECTED_ADMIN_USERNAMES', set())


@receiver(post_save, sender=GrievanceReply)
def handle_reply_posted(sender, instance, created, **kwargs):
    if created:
        send_reply_notification(instance)


@receiver(post_save, sender=Grievance)
def handle_grievance_status_changed(sender, instance, created, **kwargs):
    if not created:
        send_status_update(instance)


@receiver(pre_delete, sender=settings.AUTH_USER_MODEL)
def handle_user_deleted(sender, instance, **kwargs):
    if instance.username in get_protected_admins():
        raise PermissionDenied(f"Admin user '{instance.username}' is protected and cannot be deleted.")

    Grievance.objects.filter(student=instance).delete()
    GrievanceReply.objects.filter(admin=instance).delete()
