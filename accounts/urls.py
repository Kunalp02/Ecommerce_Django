from django.contrib import admin
from django.urls import path, include
from .import views
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
