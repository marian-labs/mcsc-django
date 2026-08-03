from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import NewsPost
from events.models import Event

def news_list(request):
    now = timezone.now()
    news_posts = NewsPost.objects.filter(is_published=True).order_by('-published_at')[:9]
    total_count = NewsPost.objects.filter(is_published=True).count()
    
    upcoming_events = Event.objects.filter(is_published=True, event_date__gte=now).order_by('event_date')[:3]
    past_events = Event.objects.filter(is_published=True, event_date__lt=now).order_by('-event_date')[:3]
    
    context = {
        'news_posts': news_posts,
        'total_count': total_count,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    }
    return render(request, 'news/news_list.html', context)

def load_more_news(request):
    offset = int(request.GET.get('offset', 9))
    limit = 9
    
    news_posts = NewsPost.objects.filter(is_published=True).order_by('-published_at')[offset:offset+limit]
    total_count = NewsPost.objects.filter(is_published=True).count()
    
    html = render_to_string('news/_news_items.html', {'news_posts': news_posts})
    has_more = (offset + limit) < total_count
    
    return JsonResponse({
        'html': html,
        'has_more': has_more
    })

def news_detail(request, slug):
    post = get_object_or_404(NewsPost, slug=slug, is_published=True)
    recent_news = NewsPost.objects.filter(is_published=True).exclude(id=post.id).order_by('-published_at')[:4]
    context = {
        'post': post,
        'recent_news': recent_news,
    }
    return render(request, 'news/news_detail.html', context)
