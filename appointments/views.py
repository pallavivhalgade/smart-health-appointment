from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment, TimeSlot
from .forms import AppointmentBookingForm, AppointmentEditForm, DoctorAppointmentUpdateForm
from accounts.models import DoctorProfile


@login_required
def book_appointment(request):
    if request.user.is_doctor:
        messages.warning(request, 'Doctors cannot book appointments. Please use a patient account.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.save()
            messages.success(request, 'Appointment booked successfully! Waiting for doctor confirmation.')
            return redirect('my_appointments')
    else:
        form = AppointmentBookingForm(user=request.user)
    
    doctors = DoctorProfile.objects.filter(is_available=True)
    context = {
        'form': form,
        'doctors': doctors,
    }
    return render(request, 'appointments/book_appointment.html', context)


@login_required
def my_appointments(request):
    if request.user.is_doctor:
        appointments = Appointment.objects.filter(doctor=request.user.doctor_profile).order_by('-date', '-time_slot')
    else:
        appointments = Appointment.objects.filter(patient=request.user).order_by('-date', '-time_slot')
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    context = {
        'appointments': appointments,
        'status_filter': status_filter,
    }
    return render(request, 'appointments/my_appointments.html', context)


@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if request.user.is_doctor:
        if appointment.doctor.user != request.user:
            messages.error(request, 'You do not have permission to view this appointment.')
            return redirect('my_appointments')
    else:
        if appointment.patient != request.user:
            messages.error(request, 'You do not have permission to view this appointment.')
            return redirect('my_appointments')
    
    context = {'appointment': appointment}
    return render(request, 'appointments/appointment_detail.html', context)


@login_required
def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Only patients can edit their own appointments
    if request.user.is_doctor or appointment.patient != request.user:
        messages.error(request, 'You do not have permission to edit this appointment.')
        return redirect('my_appointments')
    
    if not appointment.can_edit:
        messages.error(request, 'This appointment cannot be edited.')
        return redirect('appointment_detail', appointment_id=appointment_id)
    
    if request.method == 'POST':
        form = AppointmentEditForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully!')
            return redirect('appointment_detail', appointment_id=appointment_id)
    else:
        form = AppointmentEditForm(instance=appointment)
    
    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'appointments/edit_appointment.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if request.user.is_doctor:
        if appointment.doctor.user != request.user:
            messages.error(request, 'You do not have permission to cancel this appointment.')
            return redirect('my_appointments')
    else:
        if appointment.patient != request.user:
            messages.error(request, 'You do not have permission to cancel this appointment.')
            return redirect('my_appointments')
    
    if not appointment.can_cancel:
        messages.error(request, 'This appointment cannot be cancelled.')
        return redirect('appointment_detail', appointment_id=appointment_id)
    
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully.')
        return redirect('my_appointments')
    
    context = {'appointment': appointment}
    return render(request, 'appointments/cancel_appointment.html', context)


@login_required
def doctor_update_appointment(request, appointment_id):
    if not request.user.is_doctor:
        messages.error(request, 'Only doctors can update appointment status.')
        return redirect('dashboard')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor_profile)
    
    if request.method == 'POST':
        form = DoctorAppointmentUpdateForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully!')
            return redirect('appointment_detail', appointment_id=appointment_id)
    else:
        form = DoctorAppointmentUpdateForm(instance=appointment)
    
    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'appointments/doctor_update_appointment.html', context)


@login_required
def get_available_slots(request):
    """AJAX endpoint to get available time slots for a doctor on a specific date"""
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    
    if not doctor_id or not date_str:
        return JsonResponse({'slots': [], 'error': 'Missing parameters'})
    
    try:
        doctor = DoctorProfile.objects.get(id=doctor_id)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (DoctorProfile.DoesNotExist, ValueError):
        return JsonResponse({'slots': [], 'error': 'Invalid parameters'})
    
    # Get all possible slots
    all_slots = dict(TimeSlot.TIME_CHOICES)
    
    # Get booked slots for this doctor on this date
    booked_slots = Appointment.objects.filter(
        doctor=doctor,
        date=date,
        status__in=['pending', 'confirmed']
    ).values_list('time_slot', flat=True)
    
    # Filter out booked slots
    available_slots = [
        {'value': slot, 'display': display}
        for slot, display in all_slots.items()
        if slot not in booked_slots
    ]
    
    return JsonResponse({'slots': available_slots})


@login_required
def doctor_list(request):
    doctors = DoctorProfile.objects.filter(is_available=True)
    
    specialization_filter = request.GET.get('specialization', '')
    if specialization_filter:
        doctors = doctors.filter(specialization=specialization_filter)
    
    context = {
        'doctors': doctors,
        'specialization_filter': specialization_filter,
        'specializations': DoctorProfile.SPECIALIZATION_CHOICES,
    }
    return render(request, 'appointments/doctor_list.html', context)
