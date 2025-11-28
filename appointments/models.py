from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.utils import timezone
from accounts.models import User, DoctorProfile


class TimeSlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    TIME_CHOICES = [
        ('09:00', '09:00 AM'),
        ('09:30', '09:30 AM'),
        ('10:00', '10:00 AM'),
        ('10:30', '10:30 AM'),
        ('11:00', '11:00 AM'),
        ('11:30', '11:30 AM'),
        ('12:00', '12:00 PM'),
        ('14:00', '02:00 PM'),
        ('14:30', '02:30 PM'),
        ('15:00', '03:00 PM'),
        ('15:30', '03:30 PM'),
        ('16:00', '04:00 PM'),
        ('16:30', '04:30 PM'),
        ('17:00', '05:00 PM'),
    ]
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='time_slots')
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ])
    start_time = models.CharField(max_length=5, choices=TIME_CHOICES)
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ['doctor', 'day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.get_day_of_week_display()} {self.get_start_time_display()}"


class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='doctor_appointments')
    date = models.DateField()
    time_slot = models.CharField(max_length=5, choices=TimeSlot.TIME_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(help_text='Reason for appointment')
    notes = models.TextField(blank=True, help_text='Additional notes from doctor')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time_slot']
        unique_together = ['doctor', 'date', 'time_slot']

    def __str__(self):
        return f"{self.patient.get_full_name()} with Dr. {self.doctor.user.get_full_name()} on {self.date} at {self.time_slot}"

    @property
    def is_upcoming(self):
        from datetime import datetime
        appointment_datetime = datetime.combine(self.date, datetime.strptime(self.time_slot, '%H:%M').time())
        return appointment_datetime > datetime.now()

    @property
    def can_cancel(self):
        return self.status in ['pending', 'confirmed'] and self.is_upcoming

    @property
    def can_edit(self):
        return self.status in ['pending', 'confirmed'] and self.is_upcoming

    def get_time_display(self):
        time_dict = dict(TimeSlot.TIME_CHOICES)
        return time_dict.get(self.time_slot, self.time_slot)
