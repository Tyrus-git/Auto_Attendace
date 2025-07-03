from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    roll_no = models.CharField(max_length=20)
    mac_address = models.CharField(max_length=17, unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.name} ({self.roll_no})"

class Attendance(models.Model):
    mac_address = models.CharField(max_length=17, unique=True)
    last_seen = models.DateTimeField()

    def __str__(self):
        return self.mac_address

class AttendanceRecord(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # New field
    mac_address = models.CharField(max_length=20)  # New field
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.mac_address}) at {self.timestamp}"
