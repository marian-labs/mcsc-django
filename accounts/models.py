from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import PermissionDenied


class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student', db_index=True)
    can_manage_grievance = models.BooleanField(
        default=False,
        verbose_name="Can Manage Suggestions / Grievances",
        help_text="Grants access ONLY to the Suggestions/Grievance admin dashboard. Hides all other apps in Django Admin.",
    )

    def save(self, *args, **kwargs):
        if self.role == 'faculty':
            self.can_manage_grievance = True
            self.is_staff = True
        elif self.is_staff or self.is_superuser or self.role == 'admin':
            self.can_manage_grievance = True
        elif self.can_manage_grievance and not self.is_staff:
            self.is_staff = True
        super().save(*args, **kwargs)

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
