from django.core.management.base import BaseCommand
from attendance.models import Attendance, Student, AttendanceRecord
from django.utils import timezone

class Command(BaseCommand):
    help = "Tally MACs from real-time table with registered students and create permanent history"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        matched_count = 0

        real_time_macs = Attendance.objects.all()
        for entry in real_time_macs:
            student = Student.objects.filter(mac_address__iexact=entry.mac_address).first()
            if student:
                # Prevent duplicate entry within 10 minutes
                recent = AttendanceRecord.objects.filter(
                    student=student,
                    timestamp__gte=now - timezone.timedelta(seconds=30)
                ).exists()

                if not recent:
                    AttendanceRecord.objects.create(student=student,
                        timestamp=entry.last_seen,
                        name=student.name,
                        mac_address=student.mac_address)
                    matched_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Attendance recorded for {matched_count} student(s)."))
