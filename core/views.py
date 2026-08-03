from django.shortcuts import render
from django.utils import timezone
from news.models import NewsPost
from events.models import Event
from .models import CouncilInfo

def home(request):
    # Fetch news posts for ticker & bento widget
    ticker_posts = list(NewsPost.objects.filter(is_published=True).order_by('-published_at')[:6])
    news_posts = NewsPost.objects.filter(is_published=True).order_by('-published_at')[:2]
    
    # Fetch upcoming events for ticker & bento widget
    ticker_events = list(Event.objects.filter(is_published=True).order_by('event_date')[:6])
    upcoming_events = Event.objects.filter(
        is_published=True, 
        event_date__gte=timezone.now()
    ).order_by('event_date')[:3]
    
    # Build ticker slides containing 1 News item and 1 Event item
    ticker_slides = []
    max_len = max(len(ticker_posts), len(ticker_events))
    for i in range(max_len):
        slide = []
        if i < len(ticker_posts):
            slide.append({'kind': 'news', 'obj': ticker_posts[i]})
        if i < len(ticker_events):
            slide.append({'kind': 'event', 'obj': ticker_events[i]})
        if slide:
            ticker_slides.append(slide)
    
    # Fetch current council info
    council_info = CouncilInfo.objects.order_by('-academic_year').first()

    context = {
        'news_posts': news_posts,
        'ticker_slides': ticker_slides,
        'upcoming_events': upcoming_events,
        'council_info': council_info,
    }
    return render(request, 'core/home.html', context)

def about(request):
    # Fetch current council info
    council_info = CouncilInfo.objects.order_by('-academic_year').first()
    context = {
        'council_info': council_info,
    }
    return render(request, 'core/about.html', context)

