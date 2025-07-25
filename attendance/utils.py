from datetime import datetime, time, timedelta
from django.utils import timezone

def calculate_period_percentages(records, date):
    # Estimate presence minutes
    sorted_records = sorted(records, key=lambda r: r.timestamp)
    estimated_minutes = set()

    for i in range(len(sorted_records) - 1):
        start_time = sorted_records[i].timestamp.replace(second=0, microsecond=0)
        end_time = sorted_records[i + 1].timestamp.replace(second=0, microsecond=0)

        gap = int((end_time - start_time).total_seconds() / 60)
        if gap <= 5:
            current = start_time
            while current <= end_time:
                estimated_minutes.add(current)
                current += timedelta(minutes=1)

    if sorted_records:
        estimated_minutes.add(sorted_records[-1].timestamp.replace(second=0, microsecond=0))

    period_ranges = {
        'Period 1': (time(7, 0), time(8, 30)),
        'Period 2': (time(8, 30), time(10, 0)),
        'Break': (time(10, 0), time(10, 45)),  # Skip this
        'Period 3': (time(10, 45), time(12, 15)),
        'Period 4': (time(12, 15), time(13, 45)),
    }

    period_percentages = []

    for period, (start_time, end_time) in period_ranges.items():
        if period == "Break":
            continue

        start_dt = timezone.make_aware(datetime.combine(date, start_time))
        end_dt = timezone.make_aware(datetime.combine(date, end_time))
        total_minutes = int((end_dt - start_dt).total_seconds() / 60)

        present_count = 0
        current = start_dt
        while current <= end_dt:
            if current.replace(second=0, microsecond=0) in estimated_minutes:
                present_count += 1
            current += timedelta(minutes=1)

        percentage = round((present_count / total_minutes) * 100, 2)
        status = "Present" if percentage >= 75 else "Absent"

        period_percentages.append({
            'period': period,
            'percentage': percentage,
            'status': status
        })

    return period_percentages
