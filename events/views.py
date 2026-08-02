from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.cache import cache_page
from .models import Event

@cache_page(60 * 15)
def events_list(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(is_published=True, event_date__gte=now).order_by('event_date')
    past_events = Event.objects.filter(is_published=True, event_date__lt=now).order_by('-event_date')
    
    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    }
    return render(request, 'events/events_list.html', context)

@cache_page(60 * 15)
def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug, is_published=True)
    context = {
        'event': event,
    }
    return render(request, 'events/event_detail.html', context)
