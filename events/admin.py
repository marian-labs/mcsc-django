from django.contrib import admin
from django.db import models
from .models import Event, EventDate
from .widgets import Split12HourDateTimeWidget, Split12HourTimeWidget


def check_non_grievance_permission(request):
    if not request.user.is_authenticated:
        return False
    if (request.user.can_manage_grievance or request.user.role == 'faculty') and not request.user.is_superuser and request.user.role != 'admin':
        return False
    return True


class NonGrievanceAdminMixin:
    def has_module_permission(self, request):
        if not check_non_grievance_permission(request):
            return False
        return super().has_module_permission(request)


class EventDateInline(admin.TabularInline):
    model = EventDate
    extra = 0
    formfield_overrides = {
        models.TimeField: {'widget': Split12HourTimeWidget},
    }


@admin.register(Event)
class EventAdmin(NonGrievanceAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'event_date', 'venue', 'is_featured', 'is_published', 'use_default_poster')
    list_filter = ('is_published', 'is_featured', 'use_default_poster', 'event_date', 'venue')
    list_editable = ('is_featured', 'is_published')
    search_fields = ('title', 'description', 'venue')
    inlines = [EventDateInline]
    formfield_overrides = {
        models.DateTimeField: {'widget': Split12HourDateTimeWidget},
    }
