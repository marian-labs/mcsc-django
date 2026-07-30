from django.db import models

class CouncilInfo(models.Model):
    academic_year = models.CharField(max_length=20, unique=True, help_text="e.g. 2026-27")
    overview_text = models.TextField(help_text="Overview paragraph introducing MCSC")
    membership_supervisor_names = models.CharField(max_length=255, help_text="Supervising faculty names")
    election_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Council Info"
        verbose_name_plural = "Council Info"

    def __str__(self):
        return f"MCSC {self.academic_year}"
