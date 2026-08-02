from django.shortcuts import render
from django.views.decorators.cache import cache_page
from .models import Representative

@cache_page(60 * 15)
def representatives_list(request):
    latest_rep = Representative.objects.order_by('-academic_year').first()
    year_val = latest_rep.academic_year if (latest_rep and latest_rep.academic_year) else '2026-27'
    academic_year = year_val
    
    reps = Representative.objects.filter(academic_year=year_val)
    
    executives = reps.filter(position__in=['Chairman', 'Vice Chairperson']).order_by('display_order', 'name')
    other_representatives = reps.exclude(position__in=['Chairman', 'Vice Chairperson']).order_by('display_order', 'name')
    all_representatives = list(executives) + list(other_representatives)

    context = {
        'academic_year': academic_year,
        'executives': executives,
        'other_representatives': other_representatives,
        'all_representatives': all_representatives,
    }
    return render(request, 'representatives/representatives.html', context)
