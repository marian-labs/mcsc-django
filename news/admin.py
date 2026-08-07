from django.contrib import admin
from .models import NewsPost, NewsAttachment

class NewsAttachmentInline(admin.TabularInline):
    model = NewsAttachment
    extra = 1

@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'published_at')
    list_filter = ('is_published', 'published_at', 'author')
    search_fields = ('title', 'content')
    inlines = [NewsAttachmentInline]
