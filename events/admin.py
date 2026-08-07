from django.contrib import admin
from .models import Event, EventDate

class EventDateInline(admin.TabularInline):
    model = EventDate
    extra = 1

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'venue', 'is_published')
    list_filter = ('is_published', 'event_date', 'venue')
    search_fields = ('title', 'description', 'venue')
    inlines = [EventDateInline]

