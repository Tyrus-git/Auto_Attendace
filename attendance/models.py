from django.db import models

class Attendance(models.Model):
    mac_address = models.CharField(max_length=17, unique=True)
    last_seen = models.DateTimeField()

    def __str__(self):
        return self.mac_address
