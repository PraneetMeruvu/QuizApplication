from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('search/users/', views.search_users_view, name='search_users'),
]