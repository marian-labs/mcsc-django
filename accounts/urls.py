from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('push-subscribe/', views.push_subscribe, name='push_subscribe'),
    path('demo-login/', views.demo_login, name='demo_login'),
]
