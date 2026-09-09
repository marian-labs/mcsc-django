from django.db import migrations, models
from django.utils.text import slugify


def backfill_news_slugs(apps, schema_editor):
    NewsPost = apps.get_model('news', 'NewsPost')
    for post in NewsPost.objects.all():
        if not post.slug:
            base_slug = slugify(post.title, allow_unicode=True)
            if not base_slug or base_slug.strip('-') == '':
                base_slug = str(post.id) if post.id else "news"
            slug_candidate = base_slug
            counter = 1
            while NewsPost.objects.exclude(pk=post.pk).filter(slug=slug_candidate).exists():
                counter += 1
                slug_candidate = f"{base_slug}-{counter}"
            post.slug = slug_candidate
            post.save(update_fields=['slug'])


def reverse_backfill(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0007_newspost_poster_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='newspost',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, null=True, max_length=220),
        ),
        migrations.RunPython(backfill_news_slugs, reverse_backfill),
        migrations.AlterField(
            model_name='newspost',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, null=True, max_length=220, unique=True),
        ),
    ]
