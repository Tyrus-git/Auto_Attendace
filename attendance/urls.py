from django.urls import path
from . import views

urlpatterns = [
    path('', views.active_devices, name='home'),  # for /
    path('dashboard/', views.active_devices, name='dashboard'),  # optional
]
