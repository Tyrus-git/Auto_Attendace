from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Attendance
#Models for attendace
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from .models import Student
from django.contrib.auth.hashers import check_password

from django.utils.dateformat import format

from django.utils.dateformat import format
from datetime import datetime, time, timedelta
from calendar import monthrange

def active_devices(request):
    # Show only devices active in the last 20 second
    cutoff_time = timezone.now() - timedelta(seconds=20)
    devices = Attendance.objects.filter(last_seen__gte=cutoff_time).order_by('-last_seen')
    return render(request, 'attendance/dashboard.html', {
        'devices': devices,
        'now': timezone.now()
    })

#added for the login and register
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Registered successfully. Please login.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'attendance/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            student = Student.objects.filter(email=email).first()
            if student and check_password(password, student.password):
                request.session['student_id'] = student.id
                return redirect('dashboard')
            else:
                messages.error(request, '❌ Invalid email or password')
    else:
        form = LoginForm()
    return render(request, 'attendance/login.html', {'form': form})



from django.utils.dateformat import format
# from django.contrib.auth.decorators import login_required

# @login_required
def dashboard_view(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')

    student = Student.objects.get(id=student_id)
    all_records = student.attendancerecord_set.all()

    # Filter only today's records
    today = timezone.localdate()
    today_start = timezone.make_aware(datetime.combine(today, time(7, 0)))
    today_end = timezone.make_aware(datetime.combine(today, time(13, 45)))
    today_records = all_records.filter(timestamp__range=(today_start, today_end))

    # Create a presence map (set of all minute timestamps)
    presence_minutes = set(
        r.timestamp.replace(second=0, microsecond=0)
        for r in today_records
    )

    # Define period ranges
    period_ranges = {
        'Period 1': (time(7, 0), time(8, 30)),
        'Period 2': (time(8, 30), time(10, 0)),
        'Break': (time(10, 0), time(10, 45)),  # We exclude this
        'Period 3': (time(10, 45), time(12, 15)),
        'Period 4': (time(12, 15), time(13, 45)),
    }

    period_percentages = []

    for period, (start_time, end_time) in period_ranges.items():
        if period == "Break":
            continue  # skip break

        start_dt = timezone.make_aware(datetime.combine(today, start_time))
        end_dt = timezone.make_aware(datetime.combine(today, end_time))
        total_minutes = int((end_dt - start_dt).total_seconds() / 60)

        present_count = 0
        current = start_dt
        while current <= end_dt:
            if current.replace(second=0, microsecond=0) in presence_minutes:
                present_count += 1
            current += timedelta(minutes=1)

        percentage = round((present_count / total_minutes) * 100, 2)
        status = "Present" if percentage >= 75 else "Absent"  # ➕ Status logic

        period_percentages.append({
            'period': period,
            'percentage': percentage,
            'status': status  # ➕ Add status for each period
        })

    labels = [p['period'] for p in period_percentages]
    data = [p['percentage'] for p in period_percentages]

    return render(request, 'attendance/dashboard.html', {
        'student': student,
        'records': all_records.order_by('-timestamp'),
        'today': timezone.now(),
        'period_percentages': period_percentages,
        'chart_labels': labels,
        'chart_data': data,
    })


from collections import defaultdict
from django.db.models.functions import TruncDate
from .models import AttendanceRecord

from collections import defaultdict
from django.shortcuts import render, redirect
from .models import AttendanceRecord, Student


def attendance_history_view(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return redirect('login')

    records = AttendanceRecord.objects.filter(student=student)

    daily_data = defaultdict(lambda: {'period1': False, 'period2': False, 'period3': False, 'period4': False})

    for record in records:
        date = record.timestamp.date()
        hour = record.timestamp.hour
        minute = record.timestamp.minute

        # Period mapping as before
        if (hour == 7 and minute >= 0) or (7 < hour < 8) or (hour == 8 and minute < 30):
            daily_data[date]['period1'] = True
        elif (hour == 8 and minute >= 30) or (8 < hour < 10):
            daily_data[date]['period2'] = True
        elif (hour == 10 and minute >= 45) or (10 < hour < 12) or (hour == 12 and minute < 15):
            daily_data[date]['period3'] = True
        elif (hour == 12 and minute >= 15) or (12 < hour < 13) or (hour == 13 and minute <= 45):
            daily_data[date]['period4'] = True

    attendance_table = []
    for date, periods in sorted(daily_data.items(), reverse=True):
        present_count = sum(periods.values())
        percentage = round((present_count / 4) * 100)
        attendance_table.append({
            'date': date,
            'p1': '✓' if periods['period1'] else '✗',
            'p2': '✓' if periods['period2'] else '✗',
            'p3': '✓' if periods['period3'] else '✗',
            'p4': '✓' if periods['period4'] else '✗',
            'percent': f'{percentage}%',
        })

    return render(request, 'attendance/history.html', {
        'student': student,
        'attendance_table': attendance_table
    })


def logout_view(request):
    request.session.flush()
    return redirect('login')
