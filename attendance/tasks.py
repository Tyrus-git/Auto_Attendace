import threading
import time
from django.utils import timezone
from attendance.models import Attendance, AttendanceRecord, Student


def tally_attendance_loop():
    while True:
        now = timezone.now()
        real_time_macs = Attendance.objects.all()
        for entry in real_time_macs:
            student = Student.objects.filter(mac_address__iexact=entry.mac_address).first()
            if student:
                recent = AttendanceRecord.objects.filter(
                    student=student,
                    timestamp__gte=now - timezone.timedelta(seconds=60)
                ).exists()

                if not recent:
                    AttendanceRecord.objects.create(
                        student=student,
                        name=student.name,
                        mac_address=student.mac_address,
                        timestamp=entry.last_seen
                    )
        print("✅ [Auto Tally] Attendance updated.")
        time.sleep(100)  # adjust this interval as needed
