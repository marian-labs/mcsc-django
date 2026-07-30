from django.contrib import admin
from .models import Grievance, GrievanceReply, Notification

class GrievanceReplyInline(admin.StackedInline):
    model = GrievanceReply
    extra = 1

@admin.register(Grievance)
class GrievanceAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'student__username', 'student__email')
    inlines = [GrievanceReplyInline]

@admin.register(GrievanceReply)
class GrievanceReplyAdmin(admin.ModelAdmin):
    list_display = ('grievance', 'admin', 'created_at')
    search_fields = ('reply_text', 'admin__username', 'grievance__title')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'grievance', 'type', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
