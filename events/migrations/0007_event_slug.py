from django.db import migrations, models
from django.utils.text import slugify


def drop_orphaned_indexes(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("""
                DO $$
                DECLARE r RECORD;
                BEGIN
                    FOR r IN (
                        SELECT indexname FROM pg_indexes 
                        WHERE tablename = 'events_event' AND indexname LIKE '%slug%'
                    ) LOOP
                        EXECUTE 'DROP INDEX IF EXISTS ' || quote_ident(r.indexname) || ' CASCADE;';
                    END LOOP;
                END $$;
            """)


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
        migrations.RunPython(drop_orphaned_indexes, reverse_backfill),
        migrations.AddField(
            model_name='event',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, null=True, max_length=220, db_index=False),
        ),
        migrations.RunPython(backfill_event_slugs, reverse_backfill),
        migrations.AlterField(
            model_name='event',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, null=True, max_length=220, unique=True),
        ),
    ]
