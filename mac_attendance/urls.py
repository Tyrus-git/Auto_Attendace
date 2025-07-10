# mac_attendance/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect  # ⬅ import redirect

urlpatterns = [
    path('', lambda request: redirect('login')),  # ⬅ redirect root URL to register
    path('admin/', admin.site.urls),
    path('attendance/', include('attendance.urls')),  # ⬅ your app’s URLs
]
