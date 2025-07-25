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
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import datetime, time, timedelta
from .models import Student  # Make sure your Student model is correctly imported

from .utils import calculate_period_percentages

def dashboard_view(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')

    student = Student.objects.get(id=student_id)
    today = timezone.localdate()
    today_start = timezone.make_aware(datetime.combine(today, time(7, 0)))
    today_end = timezone.make_aware(datetime.combine(today, time(13, 45)))
    today_records = student.attendancerecord_set.filter(timestamp__range=(today_start, today_end))

    period_percentages = calculate_period_percentages(today_records, today)

    labels = [p['period'] for p in period_percentages]
    data = [p['percentage'] for p in period_percentages]

    return render(request, 'attendance/dashboard.html', {
        'student': student,
        'records': student.attendancerecord_set.all().order_by('-timestamp'),
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


from .utils import calculate_period_percentages

def attendance_history_view(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')

    student = Student.objects.get(id=student_id)
    all_records = student.attendancerecord_set.all()
    date_set = sorted(set(record.timestamp.date() for record in all_records), reverse=True)

    history = []

    for date in date_set:
        day_start = timezone.make_aware(datetime.combine(date, time(7, 0)))
        day_end = timezone.make_aware(datetime.combine(date, time(13, 45)))
        day_records = all_records.filter(timestamp__range=(day_start, day_end))

        period_data = calculate_period_percentages(day_records, date)
        row = {
            'date': date,
            'periods': [p['percentage'] for p in period_data]
        }
        history.append(row)

    return render(request, 'attendance/history.html', {
        'student': student,
        'history': history
    })




def logout_view(request):
    request.session.flush()
    return redirect('login')
