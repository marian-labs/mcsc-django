from django.urls import path
from . import views

urlpatterns = [
    path('', views.representatives_list, name='representatives_list'),
]
