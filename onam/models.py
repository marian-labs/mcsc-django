from django.db import models
from django.core.cache import cache

ONAM_SETTINGS_CACHE_KEY = 'onam_settings_singleton'


# ---------------------------------------------------------------------------
# Points scales
# ---------------------------------------------------------------------------
NORMAL_POINTS = {1: 5, 2: 3, 3: 2}
MAVELIKOPPAM_POINTS = {1: 10, 2: 7, 3: 5}

POSITION_CHOICES = [
    (1, '1st Place'),
    (2, '2nd Place'),
    (3, '3rd Place'),
]

GENDER_CHOICES = [
    ('',  'Open (No Gender Split)'),
    ('M', 'Boys'),
    ('F', 'Girls'),
]


# ---------------------------------------------------------------------------
# Department — one row per college department, points auto-managed by signals
# ---------------------------------------------------------------------------
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    points = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        ordering = ['-points', 'name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# OnamGame — one of the 7 championship games
# ---------------------------------------------------------------------------
class OnamGame(models.Model):
    name = models.CharField(max_length=200)
    is_mavelikoppam = models.BooleanField(
        default=False,
        help_text="Uses special Mavelikoppam point scale: 1st=10, 2nd=7, 3rd=5. "
                  "Normal games: 1st=5, 2nd=3, 3rd=2.",
    )
    has_gender_categories = models.BooleanField(
        default=False,
        help_text="Enable if this game has separate results for Boys and Girls.",
    )
    image = models.ImageField(
        upload_to='onam_games/',
        null=True, blank=True,
        help_text="Background image shown on the game card (uploaded to Supabase).",
    )
    scheduled_date = models.DateField(
        null=True, blank=True,
        help_text="Date on which this game is scheduled (shown on the event card)",
    )
    order = models.PositiveSmallIntegerField(default=0, help_text="Display order on events page")

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Onam Game'
        verbose_name_plural = 'Onam Games'

    def __str__(self):
        return self.name

    @property
    def point_scale_display(self):
        if self.is_mavelikoppam:
            return "1st: 10 pts · 2nd: 7 pts · 3rd: 5 pts"
        return "1st: 5 pts · 2nd: 3 pts · 3rd: 2 pts"

    def _get_result(self, position, gender=''):
        for r in self.results.all():
            if r.position == position and r.gender == gender:
                return r
        return None

    # ── Open (non-gendered) result helpers ──────────────────────────────────
    @property
    def result_1st(self):
        return self._get_result(1, '')

    @property
    def result_2nd(self):
        return self._get_result(2, '')

    @property
    def result_3rd(self):
        return self._get_result(3, '')

    # ── Boys result helpers ─────────────────────────────────────────────────
    @property
    def boys_result_1st(self):
        return self._get_result(1, 'M')

    @property
    def boys_result_2nd(self):
        return self._get_result(2, 'M')

    @property
    def boys_result_3rd(self):
        return self._get_result(3, 'M')

    # ── Girls result helpers ────────────────────────────────────────────────
    @property
    def girls_result_1st(self):
        return self._get_result(1, 'F')

    @property
    def girls_result_2nd(self):
        return self._get_result(2, 'F')

    @property
    def girls_result_3rd(self):
        return self._get_result(3, 'F')

    @property
    def has_any_results(self):
        return bool(self.results.all())

    # Static image fallback mapping (used when no custom image is uploaded)
    _STATIC_BG_MAP = {
        'obstacle race':        'images/onam 26/obstacle_race.webp',
        'ishtika pidutham':     'images/onam 26/brick.webp',
        'chakkil ottam relay':  'images/onam 26/odum_kuthira.webp',
        'saree draping':        'images/onam 26/saree_draping.webp',
    }

    @property
    def static_bg_image(self):
        """Return a static-file path for the card background, or None."""
        return self._STATIC_BG_MAP.get(self.name.lower().strip())


# ---------------------------------------------------------------------------
# GameResult — up to 3 results per game per gender category
# ---------------------------------------------------------------------------
class GameResult(models.Model):
    game = models.ForeignKey(OnamGame, on_delete=models.CASCADE, related_name='results')
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default='',
        blank=True,
        help_text="Leave blank for open/non-gendered events. Set to Boys or Girls for gender-split events.",
    )
    position = models.PositiveSmallIntegerField(choices=POSITION_CHOICES)
    participant_name = models.CharField(
        max_length=200, blank=True,
        help_text="Optional — student name (can be left blank)",
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='game_results',
        help_text="Department the winner represents (determines points awarded)",
    )

    class Meta:
        unique_together = [('game', 'position', 'gender')]
        ordering = ['game', 'gender', 'position']
        verbose_name = 'Game Result'
        verbose_name_plural = 'Game Results'

    @property
    def points_value(self):
        points_map = MAVELIKOPPAM_POINTS if self.game.is_mavelikoppam else NORMAL_POINTS
        return points_map.get(self.position, 0)

    def __str__(self):
        dept = self.department.name if self.department else 'No Dept'
        name = f" ({self.participant_name})" if self.participant_name else ""
        gender_label = dict(GENDER_CHOICES).get(self.gender, '')
        gender_str = f" [{gender_label}]" if gender_label else ""
        return f"{self.game.name}{gender_str} — {self.get_position_display()}: {dept}{name}"


# ---------------------------------------------------------------------------
# OnamSettings — Control overall winner announcement & settings
# ---------------------------------------------------------------------------
class OnamSettings(models.Model):
    show_overall_winner = models.BooleanField(
        default=False,
        verbose_name="Show Overall Winner",
        help_text="Check this box in admin to officially reveal the Overall Winner Department on the Live Scoreboard & Home Banner!",
    )
    announcement_date = models.CharField(
        max_length=100,
        default="August 21, 2026",
        help_text="Date string shown when the winner announcement is still pending (e.g. August 21, 2026).",
    )

    class Meta:
        verbose_name = "Onam Championship Setting"
        verbose_name_plural = "Onam Championship Settings"

    def __str__(self):
        status = "WINNER REVEALED" if self.show_overall_winner else f"Pending (Announcing {self.announcement_date})"
        return f"Onam Settings [{status}]"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(ONAM_SETTINGS_CACHE_KEY)

    @classmethod
    def get_settings(cls):
        obj = cache.get(ONAM_SETTINGS_CACHE_KEY)
        if obj is None:
            obj, _ = cls.objects.get_or_create(id=1)
            cache.set(ONAM_SETTINGS_CACHE_KEY, obj)
        return obj

