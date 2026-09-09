from django.contrib import admin
from .models import Representative


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


@admin.register(Representative)
class RepresentativeAdmin(NonGrievanceAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'position', 'category', 'academic_year', 'display_order')
    list_filter = ('academic_year', 'category')
    search_fields = ('name', 'position')
    list_editable = ('display_order',)
