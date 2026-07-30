from django.urls import path
from . import views

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('load-more/', views.load_more_news, name='load_more_news'),
    path('<slug:slug>/', views.news_detail, name='news_detail'),
]
