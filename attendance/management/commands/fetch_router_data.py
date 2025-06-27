from django.core.management.base import BaseCommand
from attendance.models import Attendance
from django.utils import timezone
import subprocess
import re
from datetime import datetime, timedelta
import platform
import concurrent.futures
import time

class Command(BaseCommand):
    help = 'Scan network for active devices and update attendance'

    def handle(self, *args, **kwargs):
        try:
            # self.stdout.write("🔍 Using default subnet: 192.168.1.x")
            subnet = "192.168.1"

            # self.stdout.write("\n📡 Scanning ARP table...")
            # self.scan_arp_table(subnet)

            self.stdout.write("\n📶 Running comprehensive ping sweep...")
            self.ping_sweep_scan(subnet)

            self.cleanup_old_entries()
        except Exception as e:
            self.stderr.write(f"❌ Error: {e}")

    def normalize_mac(self, mac):
        return mac.replace('-', ':').upper()

    def scan_arp_table(self, subnet_prefix):
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True)

        if result.returncode == 0:
            arp_lines = result.stdout.split('\n')
            macs = []

            for line in arp_lines:
                if subnet_prefix not in line:
                    continue

                mac_match = re.search(r'([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}', line)
                if mac_match:
                    mac = self.normalize_mac(mac_match.group(0))
                    if mac not in ['FF:FF:FF:FF:FF:FF', '00:00:00:00:00:00']:
                        macs.append(mac)

            if macs:
                for mac in macs:
                    Attendance.objects.update_or_create(
                        mac_address=mac,
                        defaults={"last_seen": timezone.now()}
                    )
                self.stdout.write(self.style.SUCCESS(f"🟢 Updated attendance for {len(macs)} device(s)."))
                self.stdout.write("Devices: " + ", ".join(macs))
            else:
                self.stdout.write("⚠ No valid MACs found in ARP table.")

    def ping_sweep_scan(self, network_base):
        active_ips = []
        is_windows = platform.system().lower() == 'windows'
        ping_param = '-n' if is_windows else '-c'

        def ping_ip(ip):
            try:
                result = subprocess.run(['ping', ping_param, '1', ip],
                                        capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    return ip
            except:
                pass
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(ping_ip, f"{network_base}.{i}") for i in range(1, 255)]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    active_ips.append(result)

        if active_ips:
            self.stdout.write(f"📶 Found {len(active_ips)} active IPs.")
            time.sleep(2)
            self.scan_arp_table(network_base)
        else:
            self.stdout.write("⚠ No active IPs found during ping sweep.")

    def cleanup_old_entries(self):
        cutoff = timezone.now() - timedelta(seconds=10)
        deleted, _ = Attendance.objects.filter(last_seen__lt=cutoff).delete()
        self.stdout.write(self.style.WARNING(f"🗑 Removed {deleted} stale devices."))
