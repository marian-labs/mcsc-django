from django.db import models
from django.conf import settings

class Grievance(models.Model):
    CATEGORY_CHOICES = (
        ('academics', 'Academic & Curriculum'),
        ('facilities', 'Campus Facilities'),
        ('hostel', 'Hostel & Mess'),
        ('programs', 'Programs & Events'),
        ('general', 'General Concerns'),
    )
    
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in-review', 'In Review'),
        ('resolved', 'Resolved'),
    )

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='grievances')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    attachment = models.FileField(upload_to='grievance_attachments/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.status}) - {self.student.username}"

class GrievanceReply(models.Model):
    grievance = models.ForeignKey(Grievance, on_delete=models.CASCADE, related_name='replies')
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='grievance_replies')
    reply_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name_plural = "Grievance Replies"

    def __str__(self):
        return f"Reply by {self.admin.username} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Notification(models.Model):
    TYPE_CHOICES = (
        ('reply_posted', 'Reply Posted'),
        ('status_changed', 'Status Changed'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    grievance = models.ForeignKey(Grievance, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"Notification for {self.user.username}: {self.type}"
