from django.db import models
from django.utils.text import slugify
from django.utils import timezone

class Event(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    event_date = models.DateTimeField(db_index=True, help_text="Date and time of the event")
    venue = models.CharField(max_length=200)
    poster_image = models.ImageField(upload_to='event_posters/', null=True, blank=True)
    registration_link = models.URLField(blank=True, null=True, help_text="Link to external registration form if applicable")
    is_published = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['event_date']
        indexes = [
            models.Index(fields=['is_published', 'event_date']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            queryset = Event.objects.all()
            count = 1
            while queryset.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
        super().save(*args, **kwargs)

    @property
    def is_upcoming(self):
        return self.event_date >= timezone.now()

    def __str__(self):
        return f"{self.title} on {self.event_date.strftime('%Y-%m-%d')}"
