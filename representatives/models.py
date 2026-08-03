from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.templatetags.static import static

STATIC_REP_IMAGES = {
    'richard joseph': 'richard_joseph.webp',
    'agnes sebastian': 'agnes_sebastian.webp',
    'mariya benny': 'mariya_benny.webp',
    'davis tom': 'davis_tom.webp',
    'tony kurian': 'tony_kurian.webp',
    'aromal jaimon': 'aromal_jaimon.webp',
    'arjun r': 'arjun_R.webp',
    'sneha maria sajji': 'sneha_maria_saji.webp',
    'sneha maria saji': 'sneha_maria_saji.webp',
    'fathima rifa v': 'fathima_rifa_v.webp',
    'abhishek v b': 'abhishek_vb.webp',
    'abhishek vb': 'abhishek_vb.webp',
    'clement samuel jomon': 'clement_samuel.webp',
    'clement samuel': 'clement_samuel.webp',
    'angel mariya jomon': 'angel_mariya_jomon.webp',
    'fida nazar': 'fida_nazar.webp',
    'ansel p stephen': 'Ansel_p_stephen.webp',
    'alena maria sajju': 'alena_maria_saju.webp',
    'alena maria saju': 'alena_maria_saju.webp',
    'tom p serbichan': 'tom_p_serbiachan.webp',
    'tom p serbiachan': 'tom_p_serbiachan.webp',
    'allan george aj': 'allan_george_aj.webp',
    'brillia b bose': 'brillia_b_bose.webp',
    'anita tomy': 'anita_tomy.webp',
}

class Representative(models.Model):
    CATEGORY_CHOICES = (
        ('office_bearer', 'Office Bearer'),
        ('councilor_secretary', 'Councilor & Secretary'),
        ('year_representative', 'Year & Category Representative'),
    )
    
    academic_year = models.CharField(max_length=20, db_index=True, help_text="e.g. 2026-27")
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, help_text="e.g. Chairman, Vice Chairperson, Arts Secretary, Lady Rep")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, db_index=True)
    photo = models.ImageField(upload_to='representatives/', null=True, blank=True, help_text="Upload photo or leave empty for gradient fallback")
    display_order = models.PositiveIntegerField(default=0, db_index=True, help_text="Used to sort within categories")
    
    class Meta:
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['academic_year', 'display_order']),
            models.Index(fields=['category', 'display_order']),
        ]

    def __str__(self):
        return f"{self.name} - {self.position} ({self.academic_year})"

    @property
    def photo_url(self):
        """
        Returns uploaded DB photo URL if present.
        Otherwise matches representative name against static WebP images in static/images/reps/.
        """
        if self.photo:
            try:
                return self.photo.url
            except Exception:
                pass
            
        name_key = self.name.strip().lower()
        filename = STATIC_REP_IMAGES.get(name_key)
        if not filename:
            norm_name = name_key.replace(' ', '_').replace('.', '')
            for fname in STATIC_REP_IMAGES.values():
                base_fname = fname.rsplit('.', 1)[0].lower()
                if norm_name in base_fname or base_fname in norm_name:
                    filename = fname
                    break

        if filename:
            return static(f'images/reps/{filename}')
        return None

@receiver(post_save, sender=Representative)
@receiver(post_delete, sender=Representative)
def clear_representatives_cache(sender, instance, **kwargs):
    """Automatically clear cache when representatives details are added, edited, or deleted."""
    cache.clear()


