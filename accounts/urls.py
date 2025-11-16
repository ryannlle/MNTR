from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('search/', views.search, name='search'),
    path('profile/', views.profile, name='profile'),
    path('api/autosuggest/', views.autosuggest, name='autosuggest'),
    path('top-classes/', views.top_classes, name='top_classes'),
    path('top-classes/<str:course>/', views.top_class_detail, name='top_class_detail'),
    path('top-mentors/', views.top_mentors, name='top_mentors'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('ratings/', views.ratings, name='ratings'),
    path('appointments/', views.appointments, name='appointments'),
    path('apply-mentor/', views.apply_mentor, name='apply_mentor'),
    
]
