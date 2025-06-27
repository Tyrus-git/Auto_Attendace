# attendance/sniffer.py

import os
import django
import time
from scapy.all import sniff, ARP
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings')
django.setup()

from attendance.models import Attendance

def arp_monitor_callback(pkt):
    if pkt.haslayer(ARP):
        mac = pkt.hwsrc.upper()
        if mac not in ['FF:FF:FF:FF:FF:FF', '00:00:00:00:00:00']:
            Attendance.objects.update_or_create(
                mac_address=mac,
                defaults={'last_seen': timezone.now()}
            )
            print(f"Recorded {mac} at {timezone.now()}")

if __name__ == "__main__":
    print("Starting ARP sniffer...")
    sniff(filter="arp", store=0, prn=arp_monitor_callback)
