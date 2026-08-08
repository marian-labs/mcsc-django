from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import Http404
from django.db import models
from .models import Event


def events_list(request):
    now = timezone.now()
    today = now.date()

    # An event is "upcoming" if its primary date is in future OR it has any additional date >= today
    upcoming_events = (
        Event.objects.filter(is_published=True)
        .filter(
            models.Q(event_date__gte=now) |
            models.Q(additional_dates__date__gte=today)
        )
        .distinct()
        .order_by('event_date')
        .prefetch_related('additional_dates')
    )

    # Past = primary date already passed AND no additional future dates
    past_events = (
        Event.objects.filter(is_published=True)
        .exclude(
            models.Q(event_date__gte=now) |
            models.Q(additional_dates__date__gte=today)
        )
        .distinct()
        .order_by('-event_date')
        .prefetch_related('additional_dates')
    )

    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    }
    return render(request, 'events/events_list.html', context)

def event_detail(request, slug):
    events = Event.objects.filter(is_published=True).prefetch_related('additional_dates')
    event = next((e for e in events if e.slug == slug or str(e.id) == slug), None)
    if not event:
        raise Http404("Event not found")
    context = {
        'event': event,
    }
    return render(request, 'events/event_detail.html', context)

