from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.urls import reverse
from .models import Grievance, GrievanceReply, Notification
from core.email import send_grievance_submitted, send_reply_notification, send_status_update
from pywebpush import webpush, WebPushException
import json

def send_web_push(user, title, body, url):
    from accounts.models import PushSubscription
    subscriptions = PushSubscription.objects.filter(user=user)
    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh,
                        "auth": sub.auth
                    }
                },
                data=json.dumps({
                    "title": title,
                    "body": body,
                    "url": url
                }),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_public_key=settings.VAPID_PUBLIC_KEY,
                vapid_claims={"sub": "mailto:admin@mariancollege.org"},
                ttl=86400
            )
        except WebPushException as ex:
            if ex.response and ex.response.status_code == 410:
                sub.delete()
        except Exception as e:
            print("Web push dispatch failed:", e)

@receiver(post_save, sender=Grievance)
def handle_grievance_created(sender, instance, created, **kwargs):
    """Send a confirmation email when a student submits a new grievance."""
    if created:
        send_grievance_submitted(instance)

@receiver(post_save, sender=GrievanceReply)
def handle_reply_posted(sender, instance, created, **kwargs):
    if created:
        grievance = instance.grievance
        student = grievance.student

        # 1. Create in-app Notification
        Notification.objects.create(
            user=student,
            grievance=grievance,
            type='reply_posted'
        )

        # 2. Send HTML email via Resend
        send_reply_notification(instance)

        # 3. Send Web Push Notification to the corresponding student only
        url = reverse('grievance_portal') + f"?highlight={grievance.id}"
        send_web_push(
            user=student,
            title="Grievance Update",
            body=f"An administrator replied to: {grievance.title}",
            url=url
        )

@receiver(post_save, sender=Grievance)
def handle_grievance_status_changed(sender, instance, created, **kwargs):
    if not created:
        student = instance.student

        # 1. Create in-app Notification
        Notification.objects.create(
            user=student,
            grievance=instance,
            type='status_changed'
        )

        # 2. Send HTML email via Resend
        send_status_update(instance)

        # 3. Send Web Push Notification to the corresponding student only
        url = reverse('grievance_portal') + f"?highlight={instance.id}"
        send_web_push(
            user=student,
            title="Grievance Status Update",
            body=f"Status updated to {instance.get_status_display()}: {instance.title}",
            url=url
        )
