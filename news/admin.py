from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from events.models import Event
from .models import NewsPost, NewsAttachment


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


class NewsAttachmentInline(admin.TabularInline):
    model = NewsAttachment
    extra = 1


@admin.register(NewsPost)
class NewsPostAdmin(NonGrievanceAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'author', 'event', 'use_default_poster', 'is_published', 'published_at')
    list_filter = ('is_published', 'use_default_poster', 'published_at', 'author', 'event')
    search_fields = ('title', 'content')
    inlines = [NewsAttachmentInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "author":
            kwargs["queryset"] = get_user_model().objects.filter(is_staff=True)
        elif db_field.name == "event":
            kwargs["queryset"] = Event.objects.filter(
                models.Q(use_default_poster=True) | (models.Q(poster_image__isnull=False) & ~models.Q(poster_image=''))
            ).order_by('-event_date')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
