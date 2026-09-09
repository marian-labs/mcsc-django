import re
from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.conf import settings
from django.core.exceptions import PermissionDenied
from .models import User


def get_protected_admins():
    return getattr(settings, 'PROTECTED_ADMIN_USERNAMES', set())


class AdminAddUserForm(forms.ModelForm):
    """User creation form for Django Admin: enter email & access rights directly."""
    email = forms.EmailField(
        required=True,
        help_text="Required — Must be a @mariancollege.org email address."
    )
    first_name = forms.CharField(required=False, label="First Name")
    last_name = forms.CharField(required=False, label="Last Name")
    can_manage_grievance = forms.BooleanField(
        required=False,
        label="Can Manage Suggestions / Grievances",
        help_text="Check to give access ONLY to the Suggestions/Grievance admin dashboard."
    )
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, initial='student')
    is_staff = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Designates whether user can log into the staff/admin views."
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'can_manage_grievance', 'role', 'is_staff')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email.endswith('@mariancollege.org'):
            raise forms.ValidationError("Email address must end with @mariancollege.org")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email'].strip().lower()
        base_username = email.split('@')[0]
        username = base_username
        count = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{count}"
            count += 1
        user.username = username
        user.email = email
        user.set_unusable_password()
        if user.can_manage_grievance:
            user.is_staff = True
        if commit:
            user.save()
        return user


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = AdminAddUserForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'can_manage_grievance', 'role', 'is_staff'),
        }),
    )
    fieldsets = UserAdmin.fieldsets + (
        ('MCSC Permissions & Access Rights', {'fields': ('can_manage_grievance', 'role')}),
    )
    list_display = ('username', 'full_name', 'email', 'can_manage_grievance', 'role', 'is_staff', 'is_active')
    list_filter = ('can_manage_grievance', 'role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    actions = ['block_users', 'unblock_users', 'delete_selected']

    def has_module_permission(self, request):
        if not request.user.is_authenticated:
            return False
        # If user ONLY has faculty or can_manage_grievance (and not full superuser/admin role), hide User app in Django Admin
        if (request.user.can_manage_grievance or request.user.role == 'faculty') and not request.user.is_superuser and request.user.role != 'admin':
            return False
        return super().has_module_permission(request)

    @admin.display(description="Full Name")
    def full_name(self, obj):
        raw = obj.first_name or obj.get_full_name() or obj.username
        clean = re.sub(r'\s+\d{2}[A-Z]{2,4}\d+\s*$', '', raw).strip()
        return clean or obj.username

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
