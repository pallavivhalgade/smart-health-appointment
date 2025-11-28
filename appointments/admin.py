from django.contrib import admin
from .models import Appointment, TimeSlot


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'date', 'time_slot', 'status', 'created_at']
    list_filter = ['status', 'date', 'doctor__specialization']
    search_fields = ['patient__username', 'patient__first_name', 'doctor__user__first_name', 'reason']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'start_time', 'is_available']
    list_filter = ['day_of_week', 'is_available', 'doctor__specialization']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name']
