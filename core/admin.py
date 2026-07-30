from django.contrib import admin
from .models import CouncilInfo

@admin.register(CouncilInfo)
class CouncilInfoAdmin(admin.ModelAdmin):
    list_display = ('academic_year', 'membership_supervisor_names', 'election_date')
    search_fields = ('academic_year', 'membership_supervisor_names')
