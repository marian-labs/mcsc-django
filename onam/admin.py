from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Department, OnamGame, GameResult, OnamSettings


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


@admin.register(OnamSettings)
class OnamSettingsAdmin(NonGrievanceAdminMixin, admin.ModelAdmin):
    list_display = ('__str__', 'show_overall_winner', 'announcement_date')
    list_editable = ('show_overall_winner', 'announcement_date')

    def has_add_permission(self, request):
        if OnamSettings.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False


# ---------------------------------------------------------------------------
# Department Admin — search_fields required for autocomplete_fields to work
# ---------------------------------------------------------------------------
@admin.register(Department)
class DepartmentAdmin(NonGrievanceAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'points')
    search_fields = ('name',)          # ← required for autocomplete
    ordering = ('-points', 'name')
    readonly_fields = ('points',)

    def has_add_permission(self, request):
        return True


# ---------------------------------------------------------------------------
# Helper: a fixed-position inline form (position is set server-side)
# ---------------------------------------------------------------------------
POSITION_LABELS = {1: '🥇 1st Place', 2: '🥈 2nd Place', 3: '🥉 3rd Place'}

class FixedPositionResultForm(forms.ModelForm):
    """Form that hides the position field; position is injected by the formset."""
    position_display = forms.CharField(required=False, label='Position')

    class Meta:
        model = GameResult
        fields = ['position', 'participant_name', 'department']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide raw position field
        self.fields['position'].widget = forms.HiddenInput()
        # Show a friendly read-only label instead
        pos_val = (
            self.instance.position
            if self.instance and self.instance.pk
            else self.initial.get('position', '')
        )
        self.fields['position_display'].initial = POSITION_LABELS.get(pos_val, f'Position {pos_val}')
        self.fields['position_display'].widget.attrs.update({
            'readonly': True,
            'style': 'background:transparent;border:none;font-weight:700;width:110px;cursor:default;',
        })
        # Make department searchable via Select2 / browser search
        self.fields['department'].widget.attrs.update({'style': 'min-width:180px;'})


def make_fixed_formset(gender_value, positions=(1, 2, 3)):
    """Return a BaseInlineFormSet subclass that locks position & gender per row."""
    from django.forms.models import BaseInlineFormSet

    class _FixedFormSet(BaseInlineFormSet):
        _gender = gender_value
        _positions = positions

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for i, form in enumerate(self.forms):
                if i < len(self._positions):
                    pos = self._positions[i]
                    # Pre-fill position in initial data for new forms
                    if not form.instance.pk:
                        form.initial['position'] = pos
                        form.initial['position_display'] = POSITION_LABELS.get(pos, '')
                    # Refresh display field from instance or initial
                    actual_pos = form.instance.position if form.instance.pk else pos
                    form.fields['position_display'].initial = POSITION_LABELS.get(actual_pos, '')

        def save_new(self, form, commit=True):
            obj = super().save_new(form, commit=False)
            obj.gender = self._gender
            # Derive position from form index
            idx = self.forms.index(form)
            if idx < len(self._positions):
                obj.position = self._positions[idx]
            if commit:
                obj.save()
            return obj

        def save_existing(self, form, instance, commit=True):
            obj = super().save_existing(form, instance, commit=False)
            obj.gender = self._gender
            if commit:
                obj.save()
            return obj

    return _FixedFormSet


# ---------------------------------------------------------------------------
# Inline: Open results (no gender split) — 3 fixed rows
# ---------------------------------------------------------------------------
class OpenResultInline(admin.TabularInline):
    model = GameResult
    form = FixedPositionResultForm
    formset = make_fixed_formset(gender_value='')
    max_num = 3
    extra = 3
    fields = ('position_display', 'position', 'participant_name', 'department')
    autocomplete_fields = ['department']
    verbose_name = 'Result'
    verbose_name_plural = '🏅 Results (1st · 2nd · 3rd)'
    can_delete = True
    show_change_link = False

    def get_queryset(self, request):
        return super().get_queryset(request).filter(gender='')

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            existing = GameResult.objects.filter(game=obj, gender='').count()
            return max(0, 3 - existing)
        return 3


# ---------------------------------------------------------------------------
# Inline: Boys results — 3 fixed rows
# ---------------------------------------------------------------------------
class BoysResultInline(admin.TabularInline):
    model = GameResult
    form = FixedPositionResultForm
    formset = make_fixed_formset(gender_value='M')
    max_num = 3
    extra = 3
    fields = ('position_display', 'position', 'participant_name', 'department')
    autocomplete_fields = ['department']
    verbose_name = 'Result'
    verbose_name_plural = '♂ Boys Results (1st · 2nd · 3rd)'
    can_delete = True
    show_change_link = False

    def get_queryset(self, request):
        return super().get_queryset(request).filter(gender='M')

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            existing = GameResult.objects.filter(game=obj, gender='M').count()
            return max(0, 3 - existing)
        return 3


# ---------------------------------------------------------------------------
# Inline: Girls results — 3 fixed rows
# ---------------------------------------------------------------------------
class GirlsResultInline(admin.TabularInline):
    model = GameResult
    form = FixedPositionResultForm
    formset = make_fixed_formset(gender_value='F')
    max_num = 3
    extra = 3
    fields = ('position_display', 'position', 'participant_name', 'department')
    autocomplete_fields = ['department']
    verbose_name = 'Result'
    verbose_name_plural = '♀ Girls Results (1st · 2nd · 3rd)'
    can_delete = True
    show_change_link = False

    def get_queryset(self, request):
        return super().get_queryset(request).filter(gender='F')

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            existing = GameResult.objects.filter(game=obj, gender='F').count()
            return max(0, 3 - existing)
        return 3


# ---------------------------------------------------------------------------
# OnamGame Admin
# ---------------------------------------------------------------------------
@admin.register(OnamGame)
class OnamGameAdmin(NonGrievanceAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'is_mavelikoppam', 'has_gender_categories', 'scheduled_date', 'order', 'results_count')
    list_editable = ('order', 'has_gender_categories')
    list_filter = ('is_mavelikoppam', 'has_gender_categories')
    search_fields = ('name',)

    fieldsets = (
        (None, {
            'fields': ('name', 'order', 'scheduled_date', 'image'),
        }),
        ('Scoring', {
            'fields': ('is_mavelikoppam', 'has_gender_categories'),
            'description': (
                'Enable "Has gender categories" to show separate Boys & Girls result rows below. '
                'Save first after toggling, then re-open to see the correct result sections.'
            ),
        }),
    )

    def get_inlines(self, request, obj=None):
        if obj and obj.has_gender_categories:
            return [BoysResultInline, GirlsResultInline]
        return [OpenResultInline]

    @admin.display(description='Results')
    def results_count(self, obj):
        if obj.has_gender_categories:
            boys = obj.results.filter(gender='M').count()
            girls = obj.results.filter(gender='F').count()
            return f'♂ {boys}/3  ♀ {girls}/3'
        count = obj.results.count()
        return f'{count}/3'
