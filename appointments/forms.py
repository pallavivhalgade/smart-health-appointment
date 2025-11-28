from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment, TimeSlot
from accounts.models import DoctorProfile


class AppointmentBookingForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time_slot', 'reason']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'time_slot': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your symptoms or reason for visit'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = DoctorProfile.objects.filter(is_available=True)
        self.fields['doctor'].label_from_instance = lambda obj: f"Dr. {obj.user.get_full_name()} - {obj.get_specialization_display()} (${obj.consultation_fee})"
        
        # Set minimum date to today
        self.fields['date'].widget.attrs['min'] = timezone.now().date().isoformat()
        self.fields['date'].widget.attrs['max'] = (timezone.now().date() + timedelta(days=30)).isoformat()

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < timezone.now().date():
            raise forms.ValidationError('Cannot book appointments in the past.')
        if date > timezone.now().date() + timedelta(days=30):
            raise forms.ValidationError('Cannot book appointments more than 30 days in advance.')
        return date

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        date = cleaned_data.get('date')
        time_slot = cleaned_data.get('time_slot')
        
        if doctor and date and time_slot:
            # Check if slot is already booked
            existing = Appointment.objects.filter(
                doctor=doctor,
                date=date,
                time_slot=time_slot,
                status__in=['pending', 'confirmed']
            )
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('This time slot is already booked. Please choose another.')
        
        return cleaned_data


class AppointmentEditForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    class Meta:
        model = Appointment
        fields = ['date', 'time_slot', 'reason']
        widgets = {
            'time_slot': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['min'] = timezone.now().date().isoformat()
        self.fields['date'].widget.attrs['max'] = (timezone.now().date() + timedelta(days=30)).isoformat()

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < timezone.now().date():
            raise forms.ValidationError('Cannot book appointments in the past.')
        return date

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time_slot = cleaned_data.get('time_slot')
        
        if date and time_slot and self.instance:
            existing = Appointment.objects.filter(
                doctor=self.instance.doctor,
                date=date,
                time_slot=time_slot,
                status__in=['pending', 'confirmed']
            ).exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('This time slot is already booked. Please choose another.')
        
        return cleaned_data


class DoctorAppointmentUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add notes for the patient'}),
        }
