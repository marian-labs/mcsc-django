from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import PermissionDenied


class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student', db_index=True)

    def delete(self, *args, **kwargs):
        protected = getattr(settings, 'PROTECTED_ADMIN_USERNAMES', set())
        if self.username in protected:
            raise PermissionDenied(f"Protected admin user '{self.username}' cannot be deleted.")
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.username})"


class PushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_subscriptions')
    endpoint = models.URLField(max_length=500, unique=True)
    p256dh = models.CharField(max_length=255, help_text="Browser public key")
    auth = models.CharField(max_length=255, help_text="Browser authentication secret")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Subscription for {self.user.username} ({self.endpoint[:30]}...)"
