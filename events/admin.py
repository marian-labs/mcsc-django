from django.contrib import admin
from django.db import models
from .models import Event, EventDate
from .widgets import Split12HourDateTimeWidget, Split12HourTimeWidget

class EventDateInline(admin.TabularInline):
    model = EventDate
    extra = 0
    formfield_overrides = {
        models.TimeField: {'widget': Split12HourTimeWidget},
    }

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'venue', 'use_default_poster', 'is_published')
    list_filter = ('is_published', 'use_default_poster', 'event_date', 'venue')
    search_fields = ('title', 'description', 'venue')
    inlines = [EventDateInline]
    formfield_overrides = {
        models.DateTimeField: {'widget': Split12HourDateTimeWidget},
    }

