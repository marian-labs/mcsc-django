from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'venue', 'is_published')
    list_filter = ('is_published', 'event_date', 'venue')
    search_fields = ('title', 'description', 'venue')
    prepopulated_fields = {'slug': ('title',)}
