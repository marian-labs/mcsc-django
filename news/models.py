from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
import os

class NewsPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Full news article content")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='news_posts', limit_choices_to={'is_staff': True})
    event = models.ForeignKey('events.Event', on_delete=models.SET_NULL, null=True, blank=True, related_name='news_posts', help_text="Optionally link an event to share its poster image with this news post")
    is_published = models.BooleanField(default=True, db_index=True)
    published_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['is_published', '-published_at']),
        ]

    # Title dynamically generated as URL slug
    @property
    def slug(self):
        s = slugify(self.title, allow_unicode=True)
        if not s or s.strip('-') == '':
            return str(self.id) if self.id else "news"
        return s

    @property
    def poster_image(self):
        if self.event and self.event.poster_image:
            return self.event.poster_image
        return None

    def __str__(self):
        return self.title

class NewsAttachment(models.Model):
    FILE_TYPE_CHOICES = (
        ('image', 'Image'),
        ('document', 'Document'),
    )
    news_post = models.ForeignKey(NewsPost, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='news_attachments/')
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default='document')

    @property
    def generic_filename(self):
        if not self.file or not self.file.name:
            return "attachment"
        ext = os.path.splitext(self.file.name)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
            return f"image{ext if ext else '.jpg'}"
        elif ext in ['.pdf']:
            return "report.pdf"
        elif ext in ['.doc', '.docx']:
            return f"report{ext}"
        elif ext:
            return f"document{ext}"
        return "attachment"

    def __str__(self):
        return f"Attachment for {self.news_post.title} ({self.file_type})"
