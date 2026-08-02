from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.conf import settings
from django.core.exceptions import PermissionDenied
from .models import User


def get_protected_admins():
    return getattr(settings, 'PROTECTED_ADMIN_USERNAMES', set())


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('MCSC Role', {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    actions = ['block_users', 'unblock_users', 'delete_selected']

    @admin.action(description="🚫 Block / Deactivate selected users")
    def block_users(self, request, queryset):
        protected = queryset.filter(username__in=get_protected_admins())
        if protected.exists():
            messages.error(request, "Protected superusers cannot be blocked.")
            queryset = queryset.exclude(username__in=get_protected_admins())

        count = queryset.update(is_active=False)
        self.message_user(request, f"Successfully blocked {count} user(s). They can no longer log in or access the site.", messages.SUCCESS)

    @admin.action(description="✅ Unblock / Activate selected users")
    def unblock_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"Successfully unblocked {count} user(s).", messages.SUCCESS)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.username in get_protected_admins():
            return False
        return super().has_delete_permission(request, obj)

    def delete_model(self, request, obj):
        if obj.username in get_protected_admins():
            raise PermissionDenied(f"Admin user '{obj.username}' is protected and cannot be deleted.")
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        protected_list = get_protected_admins()
        protected = queryset.filter(username__in=protected_list)
        if protected.exists():
            protected_names = ", ".join(protected.values_list('username', flat=True))
            messages.error(request, f"Cannot delete protected admin user(s): {protected_names}.")
            queryset = queryset.exclude(username__in=protected_list)

        if queryset.exists():
            super().delete_queryset(request, queryset)
