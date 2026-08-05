import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponseForbidden, FileResponse, Http404
from django.db.models import Count
from django.contrib import messages
from django.conf import settings
from core.ratelimit import ratelimit
from .models import Grievance, GrievanceReply, Notification
from .forms import GrievanceForm

@login_required
@ratelimit(rate='5/5m', key='user_or_ip')
def grievance_portal(request):
    # If the user is admin, redirect to the admin dashboard
    if request.user.role == 'admin' or request.user.is_staff:
        return redirect('grievance_admin_dashboard')
        
    student = request.user
    my_grievances = Grievance.objects.filter(student=student).order_by('-created_at')
    
    # Calculate stats
    total_submitted = my_grievances.count()
    in_review = my_grievances.filter(status='in-review').count()
    resolved = my_grievances.filter(status='resolved').count()
    
    if request.method == 'POST':
        form = GrievanceForm(request.POST, request.FILES)
        if form.is_valid():
            grievance = form.save(commit=False)
            grievance.student = student
            grievance.save()
            messages.success(request, "Your grievance has been submitted successfully.")
            return redirect('grievance_detail', pk=grievance.pk)
    else:
        form = GrievanceForm()
        
    # Fetch notifications & unread updates
    unread_notifications_count = Notification.objects.filter(user=student, is_read=False).count()
    latest_notification = Notification.objects.filter(user=student, is_read=False).order_by('-created_at').first()
        
    context = {
        'form': form,
        'my_grievances': my_grievances,
        'total_submitted': total_submitted,
        'in_review': in_review,
        'resolved': resolved,
        'latest_notification': latest_notification,
        'unread_notifications_count': unread_notifications_count,
        'has_updates': unread_notifications_count > 0,
    }
    return render(request, 'grievances/submit.html', context)

@login_required
def grievance_detail(request, pk):
    # View details of a single grievance including replies
    grievance = get_object_or_404(Grievance, pk=pk)
    # Check authorization
    if grievance.student != request.user and not request.user.is_staff and request.user.role != 'admin':
        return HttpResponseForbidden("You are not authorized to view this grievance.")
    
    # Mark unread notifications as read if student views the ticket
    if request.user == grievance.student:
        Notification.objects.filter(user=request.user, grievance=grievance, is_read=False).update(is_read=True)
        
    if request.method == 'POST' and (request.user.is_staff or request.user.role == 'admin'):
        reply_text = request.POST.get('reply_text')
        if reply_text:
            GrievanceReply.objects.create(
                grievance=grievance,
                admin=request.user,
                reply_text=reply_text
            )
            # Update status if passed
            new_status = request.POST.get('status')
            if new_status in dict(Grievance.STATUS_CHOICES):
                grievance.status = new_status
                grievance.save()
            messages.success(request, "Reply posted successfully.")
            return redirect('grievance_detail', pk=pk)
            
    context = {
        'grievance': grievance,
        'replies': grievance.replies.all(),
        'status_choices': Grievance.STATUS_CHOICES,
    }
    return render(request, 'grievances/detail.html', context)

@staff_member_required
def admin_dashboard(request):
    all_grievances = Grievance.objects.all().order_by('-created_at')
    
    # Simple stats for template
    stats = {
        'total': all_grievances.count(),
        'open': all_grievances.filter(status='open').count(),
        'in_review': all_grievances.filter(status='in-review').count(),
        'resolved': all_grievances.filter(status='resolved').count(),
    }
    
    context = {
        'grievances': all_grievances,
        'stats': stats,
    }
    return render(request, 'grievances/admin_dashboard.html', context)

@staff_member_required
def api_stats(request):
    # Returns aggregate counts for Chart.js
    status_counts = list(
        Grievance.objects.values('status')
        .annotate(count=Count('id'))
    )
    category_counts = list(
        Grievance.objects.values('category')
        .annotate(count=Count('id'))
    )
    
    # Format choice display names
    status_map = dict(Grievance.STATUS_CHOICES)
    category_map = dict(Grievance.CATEGORY_CHOICES)
    
    for item in status_counts:
        item['label'] = status_map.get(item['status'], item['status'])
        
    for item in category_counts:
        item['label'] = category_map.get(item['category'], item['category'])
        
    return JsonResponse({
        'status_data': status_counts,
        'category_data': category_counts,
    })

@login_required
def download_attachment(request, pk):
    grievance = get_object_or_404(Grievance, pk=pk)
    if grievance.student != request.user and not request.user.is_staff and request.user.role != 'admin':
        return HttpResponseForbidden("You are not authorized to access this attachment.")
    
    if not grievance.attachment:
        raise Http404("No attachment associated with this grievance.")
        
    try:
        if settings.USE_SUPABASE_STORAGE:
            return redirect(grievance.attachment.url)

        if grievance.attachment.storage.exists(grievance.attachment.name):
            file_handle = grievance.attachment.storage.open(grievance.attachment.name, 'rb')
            return FileResponse(
                file_handle,
                as_attachment=True,
                filename=os.path.basename(grievance.attachment.name)
            )
        return redirect(grievance.attachment.url)
    except Exception:
        if grievance.attachment and hasattr(grievance.attachment, 'url'):
            return redirect(grievance.attachment.url)
        raise Http404("Attachment file does not exist.")
