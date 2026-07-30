from django.contrib import admin
from .models import Representative

@admin.register(Representative)
class RepresentativeAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'category', 'academic_year', 'display_order')
    list_filter = ('academic_year', 'category')
    search_fields = ('name', 'position')
    list_editable = ('display_order',)
