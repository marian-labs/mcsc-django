from django.urls import path
from . import views

urlpatterns = [
    path('', views.events_list, name='events_list'),
    path('<slug:slug>/', views.event_detail, name='event_detail'),
]
