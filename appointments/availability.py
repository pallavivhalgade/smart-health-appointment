from datetime import datetime, timedelta
from django.utils import timezone
from .models import Appointment, TimeSlot


def validate_booking_date(date):
    today = timezone.localdate()
    if date < today:
        return 'Cannot book appointments in the past.'
    if date > today + timedelta(days=30):
        return 'Cannot book appointments more than 30 days in advance.'
    return None


def slot_is_future(date, time_slot):
    starts_at = timezone.make_aware(
        datetime.combine(date, datetime.strptime(time_slot, '%H:%M').time()),
        timezone.get_current_timezone(),
    )
    return starts_at > timezone.now()


def available_slots(doctor, date):
    if not doctor.is_available or validate_booking_date(date):
        return []
    booked = set(Appointment.objects.filter(
        doctor=doctor, date=date, status__in=['pending', 'confirmed'],
    ).values_list('time_slot', flat=True))
    return [
        {'value': slot, 'display': label}
        for slot, label in TimeSlot.TIME_CHOICES
        if slot not in booked and slot_is_future(date, slot)
    ]
