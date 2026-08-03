from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.conf import settings
from core.ratelimit import ratelimit
from .models import PushSubscription

@ratelimit(rate='5/m', key='ip')
def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or 'grievance_portal'
    
    if request.user.is_authenticated:
        return redirect(next_url)
        
    if request.method == 'POST':
        # Local password login (mainly for local testing and admin/staff users)
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid login credentials.")
    else:
        form = AuthenticationForm()
        
    context = {
        'form': form,
        'next': next_url,
        'debug': settings.DEBUG,
    }
    return render(request, 'accounts/login.html', context)

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
@ratelimit(rate='10/m', key='user_or_ip')
def push_subscribe(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            endpoint = data.get('endpoint')
            keys = data.get('keys', {})
            p256dh = keys.get('p256dh')
            auth = keys.get('auth')
            
            if not endpoint or not p256dh or not auth:
                print("Invalid push subscription registration request (missing parameters):", data)
                return JsonResponse({'status': 'error', 'message': 'Missing endpoint or key credentials.'}, status=400)

            PushSubscription.objects.update_or_create(
                user=request.user,
                endpoint=endpoint,
                defaults={
                    'p256dh': p256dh,
                    'auth': auth
                }
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            import traceback
            print("Push subscription view error:")
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
