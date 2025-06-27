from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Attendance

def active_devices(request):
    # Show only devices active in the last 20 second
    cutoff_time = timezone.now() - timedelta(seconds=20)
    devices = Attendance.objects.filter(last_seen__gte=cutoff_time).order_by('-last_seen')
    return render(request, 'attendance/dashboard.html', {
        'devices': devices,
        'now': timezone.now()
    })
