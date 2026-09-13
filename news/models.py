from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
import os

DEFAULT_POSTER_PATH = 'general/mcsc_logo.png'

class NewsPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Full news article content")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='news_posts', limit_choices_to={'is_staff': True})
    event = models.ForeignKey('events.Event', on_delete=models.SET_NULL, null=True, blank=True, related_name='news_posts', help_text="Optionally link an event to share its poster image with this news post")
    poster_image = models.ImageField(upload_to='news_posters/', null=True, blank=True, help_text="Upload custom poster image for this news article")
    use_default_poster = models.BooleanField(default=False, help_text="Use general MCSC Logo as news poster (instead of custom poster image)")
    slug = models.SlugField(max_length=220, unique=True, blank=True, null=True, db_index=True, allow_unicode=True)
    is_published = models.BooleanField(default=True, db_index=True)
    published_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['is_published', '-published_at']),
        ]

    def generate_unique_slug(self):
        base_slug = slugify(self.title, allow_unicode=True)
        if not base_slug or base_slug.strip('-') == '':
            base_slug = str(self.id) if self.id else "news"
        slug_candidate = base_slug
        counter = 1
        qs = NewsPost.objects.all()
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        while qs.filter(slug=slug_candidate).exists():
            counter += 1
            slug_candidate = f"{base_slug}-{counter}"
        return slug_candidate

    @property
    def poster_url(self):
        if self.poster_image:
            try:
                return self.poster_image.url
            except Exception:
                pass
        if self.event and self.event.poster_url:
            return self.event.poster_url
        if self.use_default_poster:
            try:
                return f"{settings.STATIC_URL}images/mcsc_logo.png"
            except Exception:
                return "/static/images/mcsc_logo.png"
        return None

    def clean(self):
        super().clean()
        if self.poster_image:
            self.use_default_poster = False

    def save(self, *args, **kwargs):
        if self.poster_image:
            self.use_default_poster = False
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)

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

    def save(self, *args, **kwargs):
        if self.file and self.file.name:
            ext = os.path.splitext(self.file.name)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
                self.file_type = 'image'
            elif ext in ['.pdf', '.doc', '.docx', '.txt', '.zip', '.rar']:
                self.file_type = 'document'
        super().save(*args, **kwargs)

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
