from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse, Http404
from django.template.loader import render_to_string
from .models import NewsPost

def news_list(request):
    news_posts = NewsPost.objects.filter(is_published=True).order_by('-published_at')[:9]
    total_count = NewsPost.objects.filter(is_published=True).count()
    
    context = {
        'news_posts': news_posts,
        'total_count': total_count,
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
    post = NewsPost.objects.filter(is_published=True, slug=slug).first()
    if not post:
        try:
            post = NewsPost.objects.filter(is_published=True, pk=int(slug)).first()
        except (ValueError, TypeError):
            post = None
    if not post:
        raise Http404("News post not found")
    recent_news = NewsPost.objects.filter(is_published=True).exclude(id=post.id).order_by('-published_at')[:4]
    context = {
        'post': post,
        'recent_news': recent_news,
    }
    return render(request, 'news/news_detail.html', context)
