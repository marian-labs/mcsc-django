from django.contrib import admin
from .models import Grievance, GrievanceReply, Notification


def has_grievance_permission(request):
    if not request.user.is_authenticated:
        return False
    return request.user.is_superuser or request.user.role in ['admin', 'faculty'] or request.user.is_staff or request.user.can_manage_grievance


class GrievanceAdminPermissionMixin:
    def has_module_permission(self, request):
        return has_grievance_permission(request)

    def has_view_permission(self, request, obj=None):
        return has_grievance_permission(request)

    def has_change_permission(self, request, obj=None):
        return has_grievance_permission(request)


class GrievanceReplyInline(admin.StackedInline):
    model = GrievanceReply
    extra = 1


@admin.register(Grievance)
class GrievanceAdmin(GrievanceAdminPermissionMixin, admin.ModelAdmin):
    list_display = ('title', 'student', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'student__username', 'student__email')
    inlines = [GrievanceReplyInline]
    actions = ['delete_selected']


@admin.register(GrievanceReply)
class GrievanceReplyAdmin(GrievanceAdminPermissionMixin, admin.ModelAdmin):
    list_display = ('grievance', 'admin', 'created_at')
    search_fields = ('reply_text', 'admin__username', 'grievance__title')


@admin.register(Notification)
class NotificationAdmin(GrievanceAdminPermissionMixin, admin.ModelAdmin):
    list_display = ('user', 'grievance', 'type', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
