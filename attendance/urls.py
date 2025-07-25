from django.urls import path
from . import views
from .views import register_view, login_view, dashboard_view, logout_view



urlpatterns = [
    path('', views.active_devices, name='home'),  # for /
    #path('dashboard/', views.active_devices, name='dashboard'),  # optional

    #added for the login and register
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('attendance-history/', views.attendance_history_view, name='attendance_history'),
    
]
