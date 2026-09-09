from django.shortcuts import render
from django.utils import timezone
from news.models import NewsPost
from events.models import Event
from .models import CouncilInfo

def home(request):
    # Fetch news posts for ticker & bento widget
    ticker_posts = list(NewsPost.objects.filter(is_published=True).order_by('-published_at')[:6])
    news_posts = NewsPost.objects.filter(is_published=True).order_by('-published_at')[:2]
    
    now = timezone.now()
    today = now.date()
    from django.db import models as db_models

    # Fetch upcoming events for ticker & bento widget (including multi-day events until last date)
    upcoming_events_qs = (
        Event.objects.filter(is_published=True)
        .filter(
            db_models.Q(event_date__gte=now) |
            db_models.Q(additional_dates__date__gte=today)
        )
        .distinct()
        .order_by('event_date')
        .prefetch_related('additional_dates')
    )
    ticker_events = list(upcoming_events_qs[:6])
    upcoming_events = list(upcoming_events_qs[:3])
    
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

    # Onam Championship summary for home banner
    try:
        from onam.models import Department, OnamSettings
        onam_leader = Department.objects.filter(points__gt=0).order_by('-points', 'name').first()
        onam_total_departments = Department.objects.filter(points__gt=0).count()
        onam_settings = OnamSettings.get_settings()
    except Exception:
        onam_leader = None
        onam_total_departments = 0
        onam_settings = None

    context = {
        'news_posts': news_posts,
        'ticker_slides': ticker_slides,
        'upcoming_events': upcoming_events,
        'council_info': council_info,
        'onam_leader': onam_leader,
        'onam_total_departments': onam_total_departments,
        'onam_settings': onam_settings,
    }
    return render(request, 'core/home.html', context)

def about(request):
    # Fetch current council info
    council_info = CouncilInfo.objects.order_by('-academic_year').first()
    context = {
        'council_info': council_info,
    }
    return render(request, 'core/about.html', context)

