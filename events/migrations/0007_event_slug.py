from django.db import migrations, models
from django.utils.text import slugify


def backfill_event_slugs(apps, schema_editor):
    Event = apps.get_model('events', 'Event')
    for event in Event.objects.all():
        if not event.slug:
            base_slug = slugify(event.title, allow_unicode=True)
            if not base_slug or base_slug.strip('-') == '':
                base_slug = str(event.id) if event.id else "event"
            slug_candidate = base_slug
            counter = 1
            while Event.objects.exclude(pk=event.pk).filter(slug=slug_candidate).exists():
                counter += 1
                slug_candidate = f"{base_slug}-{counter}"
            event.slug = slug_candidate
            event.save(update_fields=['slug'])


def reverse_backfill(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_add_is_featured_to_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, null=True, max_length=220),
        ),
        migrations.RunPython(backfill_event_slugs, reverse_backfill),
        migrations.AlterField(
            model_name='event',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, null=True, max_length=220, unique=True),
        ),
    ]
