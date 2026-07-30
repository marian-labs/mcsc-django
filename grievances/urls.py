from django.urls import path
from . import views

urlpatterns = [
    path('', views.grievance_portal, name='grievance_portal'),
    path('dashboard/', views.admin_dashboard, name='grievance_admin_dashboard'),
    path('grievance/<int:pk>/', views.grievance_detail, name='grievance_detail'),
    path('api/stats/', views.api_stats, name='grievance_api_stats'),
]
