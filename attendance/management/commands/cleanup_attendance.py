# attendance/management/commands/cleanup_attendance.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from attendance.models import Attendance

class Command(BaseCommand):
    help = 'Remove stale attendance entries'

    def handle(self, *args, **kwargs):
        cutoff = timezone.now() - timedelta(seconds=20)
        deleted, _ = Attendance.objects.filter(last_seen__lt=cutoff).delete()
        self.stdout.write(f"🗑 Removed {deleted} stale entries")
