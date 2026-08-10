from django.db import models
from django.utils.text import slugify
from django.utils import timezone

DEFAULT_POSTER_PATH = 'general/mcsc_logo.png'

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField(db_index=True, help_text="Date and time of the event")
    venue = models.CharField(max_length=200)
    poster_image = models.ImageField(upload_to='event_posters/', null=True, blank=True, help_text="Upload custom poster image")
    use_default_poster = models.BooleanField(default=False, help_text="Use general MCSC Logo as poster (instead of custom poster image)")
    registration_link = models.URLField(blank=True, null=True, help_text="Link to external registration form if applicable")
    is_published = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True, help_text="Mark as featured — shows a 'Featured' badge on the event card")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['event_date']
        indexes = [
            models.Index(fields=['is_published', 'event_date']),
        ]

    # Title dynamically generated as URL slug
    @property
    def slug(self):
        s = slugify(self.title, allow_unicode=True)
        if not s or s.strip('-') == '':
            return str(self.id) if self.id else "event"
        return s

    @property
    def poster_url(self):
        if self.use_default_poster:
            try:
                from django.conf import settings
                return f"{settings.STATIC_URL}images/mcsc_logo.png"
            except Exception:
                return "/static/images/mcsc_logo.png"
        if self.poster_image:
            try:
                return self.poster_image.url
            except Exception:
                pass
        return None

    @property
    def is_upcoming(self):
        """Returns True if the event hasn't fully finished yet.
        For multi-day events, stays True until the last additional date has passed.
        """
        now = timezone.now()
        # Check if any additional date is still in the future or today
        if self.additional_dates.filter(date__gte=now.date()).exists():
            return True
        return self.event_date >= now

    def clean(self):
        super().clean()
        if self.use_default_poster and self.poster_image:
            self.poster_image = None

    def save(self, *args, **kwargs):
        if self.use_default_poster and self.poster_image:
            self.poster_image = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} on {self.event_date.strftime('%Y-%m-%d')}"

# NEW: Optional Multiple Dates for Events
class EventDate(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='additional_dates')
    date = models.DateField(help_text="Additional event date")
    time = models.TimeField(null=True, blank=True, help_text="Optional event time (12-hour format e.g. 02:20 PM)")
    label = models.CharField(max_length=100, blank=True, help_text="Optional label e.g., 'Day 2' or 'Session 2'")

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        time_str = f", {self.time.strftime('%I:%M %p')}" if self.time else ""
        if self.label:
            return f"{self.label}: {self.date.strftime('%Y-%m-%d')}{time_str}"
        return f"{self.date.strftime('%Y-%m-%d')}{time_str}"

