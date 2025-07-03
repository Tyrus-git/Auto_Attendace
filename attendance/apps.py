
from django.apps import AppConfig
import threading

class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attendance'
# attendance/apps.py

from django.apps import AppConfig

class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attendance'

    def ready(self):
        # Start the scheduler on app ready
        from . import scheduler
        scheduler.start()
    
    #Start the attendace tally loop
        from attendance.tasks import tally_attendance_loop
        thread = threading.Thread(target=tally_attendance_loop, daemon=True)
        thread.start()