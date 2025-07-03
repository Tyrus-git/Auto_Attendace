from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from .models import Attendance
#Models for attendace
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from .models import Student
from django.contrib.auth.hashers import check_password


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

def dashboard_view(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')

    student = Student.objects.get(id=student_id)
    records = student.attendancerecord_set.all().order_by('-timestamp')
    return render(request, 'attendance/dashboard.html', {
        'student': student,
        'records': records
    })

def logout_view(request):
    request.session.flush()
    return redirect('login')
