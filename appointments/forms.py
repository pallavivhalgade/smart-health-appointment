from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Appointment, TimeSlot
from accounts.models import DoctorProfile
from .availability import slot_is_future, validate_booking_date


class SchedulingValidationMixin:
    def clean_date(self):
        date = self.cleaned_data['date']
        error = validate_booking_date(date)
        if error:
            raise forms.ValidationError(error)
        return date

    def clean(self):
        cleaned = super().clean()
        date, slot = cleaned.get('date'), cleaned.get('time_slot')
        if date and slot and not slot_is_future(date, slot):
            self.add_error('time_slot', 'Choose a time slot that has not already passed.')
        return cleaned

class AppointmentBookingForm(SchedulingValidationMixin, forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    doctor = forms.ModelChoiceField(
        queryset=DoctorProfile.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Select a doctor",
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

        self.fields['doctor'].queryset = DoctorProfile.objects.filter(is_available=True).select_related('user')
        self.fields['doctor'].label_from_instance = lambda obj: f"Dr. {obj.user.get_full_name()} - {obj.get_specialization_display()}"


        # Set date limits
        self.fields['date'].widget.attrs['min'] = timezone.localdate().isoformat()
        self.fields['date'].widget.attrs['max'] = (timezone.localdate() + timedelta(days=30)).isoformat()


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


class AppointmentEditForm(SchedulingValidationMixin, forms.ModelForm):
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
        self.fields['date'].widget.attrs['min'] = timezone.localdate().isoformat()
        self.fields['date'].widget.attrs['max'] = (timezone.localdate() + timedelta(days=30)).isoformat()

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
