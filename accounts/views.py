from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .forms import (
    PatientRegistrationForm, DoctorRegistrationForm, CustomLoginForm,
    PatientProfileForm, DoctorProfileForm, UserUpdateForm
)
from .models import DoctorProfile
from appointments.models import Appointment


def home(request):
    doctors = DoctorProfile.objects.filter(is_available=True)[:6]
    context = {
        'doctors': doctors,
        'total_doctors': DoctorProfile.objects.filter(is_available=True).count(),
    }
    return render(request, 'home.html', context)


def register_patient(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to SmartHealth.')
            return redirect('dashboard')
    else:
        form = PatientRegistrationForm()
    return render(request, 'accounts/register_patient.html', {'form': form})


def register_doctor(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to SmartHealth.')
            return redirect('dashboard')
    else:
        form = DoctorRegistrationForm()
    return render(request, 'accounts/register_doctor.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().first_name or form.get_user().username}!')
        return super().form_valid(form)


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}
    
    if user.is_doctor:
        try:
            doctor_profile = user.doctor_profile
            upcoming_appointments = Appointment.objects.filter(
                doctor=doctor_profile,
                status='confirmed'
            ).order_by('date', 'time_slot')[:5]
            pending_appointments = Appointment.objects.filter(
                doctor=doctor_profile,
                status='pending'
            ).order_by('date', 'time_slot')
            total_appointments = Appointment.objects.filter(doctor=doctor_profile).count()
            context.update({
                'doctor_profile': doctor_profile,
                'upcoming_appointments': upcoming_appointments,
                'pending_appointments': pending_appointments,
                'total_appointments': total_appointments,
            })
        except DoctorProfile.DoesNotExist:
            pass
        return render(request, 'accounts/doctor_dashboard.html', context)
    else:
        try:
            patient_profile = user.patient_profile
            my_appointments = Appointment.objects.filter(
                patient=user
            ).order_by('-date', '-time_slot')[:5]
            upcoming_appointments = Appointment.objects.filter(
                patient=user,
                status__in=['confirmed', 'pending']
            ).order_by('date', 'time_slot')[:5]
            context.update({
                'patient_profile': patient_profile,
                'my_appointments': my_appointments,
                'upcoming_appointments': upcoming_appointments,
            })
        except:
            pass
        return render(request, 'accounts/patient_dashboard.html', context)


@login_required
def profile(request):
    user = request.user
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        
        if user.is_doctor:
            profile_form = DoctorProfileForm(request.POST, instance=user.doctor_profile)
        else:
            profile_form = PatientProfileForm(request.POST, instance=user.patient_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=user)
        if user.is_doctor:
            profile_form = DoctorProfileForm(instance=user.doctor_profile)
        else:
            profile_form = PatientProfileForm(instance=user.patient_profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile.html', context)
