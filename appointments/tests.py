from datetime import timedelta
from unittest.mock import patch
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from accounts.models import DoctorProfile, PatientProfile, User
from .forms import AppointmentBookingForm, AppointmentEditForm
from .models import Appointment


class AppointmentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.patient = User.objects.create_user(username='patient')
        PatientProfile.objects.create(user=cls.patient)
        cls.other = User.objects.create_user(username='other')
        doctor_user = User.objects.create_user(username='doctor', user_type='doctor')
        cls.doctor = DoctorProfile.objects.create(user=doctor_user, specialization='general_physician', license_number='TEST-1')
        cls.date = timezone.localdate() + timedelta(days=1)

    def booking_data(self, **updates):
        data = {'doctor': self.doctor.pk, 'date': self.date, 'time_slot': '09:00', 'reason': 'Test appointment'}
        data.update(updates)
        return data

    def appointment(self, **updates):
        data = self.booking_data()
        data.update(doctor=self.doctor, patient=self.patient)
        data.update(updates)
        return Appointment.objects.create(**data)

    def test_cancelled_slot_can_be_booked_again(self):
        self.appointment(status='cancelled')
        self.client.force_login(self.patient)
        response = self.client.post(reverse('book_appointment'), self.booking_data())
        self.assertRedirects(response, reverse('my_appointments'))
        self.assertEqual(Appointment.objects.filter(status='pending').count(), 1)

    def test_database_rejects_duplicate_active_slot(self):
        self.appointment()
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.appointment(patient=self.other)

    def test_form_rejects_booked_slot(self):
        self.appointment()
        form = AppointmentBookingForm(self.booking_data())
        self.assertFalse(form.is_valid())
        self.assertIn('already booked', str(form.errors))

    def test_unavailable_doctor_cannot_be_booked(self):
        self.doctor.is_available = False
        self.doctor.save()
        form = AppointmentBookingForm(self.booking_data())
        self.assertFalse(form.is_valid())
        self.assertIn('doctor', form.errors)

    def test_booking_and_edit_share_date_limits(self):
        appointment = self.appointment()
        for date in (timezone.localdate() - timedelta(days=1), self.date + timedelta(days=31)):
            for form in (AppointmentBookingForm(self.booking_data(date=date)), AppointmentEditForm(self.booking_data(date=date), instance=appointment)):
                with self.subTest(date=date, form=type(form).__name__):
                    self.assertFalse(form.is_valid())
                    self.assertIn('date', form.errors)

    @patch('appointments.forms.slot_is_future', return_value=False)
    def test_elapsed_slot_rejected_by_both_forms(self, unused):
        appointment = self.appointment()
        for form in (AppointmentBookingForm(self.booking_data()), AppointmentEditForm(self.booking_data(), instance=appointment)):
            self.assertFalse(form.is_valid())
            self.assertIn('time_slot', form.errors)

    def test_other_patient_cannot_access_appointment(self):
        appointment = self.appointment()
        self.client.force_login(self.other)
        for route in ('appointment_detail', 'edit_appointment', 'cancel_appointment'):
            self.assertRedirects(self.client.get(reverse(route, args=[appointment.pk])), reverse('my_appointments'))

    def test_slots_endpoint_handles_invalid_uuid(self):
        self.client.force_login(self.patient)
        response = self.client.get(reverse('get_available_slots'), {'doctor_id': 'invalid', 'date': self.date})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['slots'], [])

    def test_slots_track_cancellation(self):
        self.client.force_login(self.patient)
        appointment = self.appointment()
        params = {'doctor_id': self.doctor.pk, 'date': self.date}
        slots = self.client.get(reverse('get_available_slots'), params).json()['slots']
        self.assertNotIn('09:00', [slot['value'] for slot in slots])
        appointment.status = 'cancelled'
        appointment.save()
        slots = self.client.get(reverse('get_available_slots'), params).json()['slots']
        self.assertIn('09:00', [slot['value'] for slot in slots])

    def test_slot_race_returns_form_error(self):
        self.client.force_login(self.patient)
        with patch('appointments.models.Appointment.save', side_effect=IntegrityError('slot conflict')):
            response = self.client.post(reverse('book_appointment'), self.booking_data())
        self.assertContains(response, 'just booked')
        self.assertEqual(Appointment.objects.count(), 0)

    def test_authenticated_pages_render(self):
        self.client.force_login(self.patient)
        appointment = self.appointment()
        for route in ('dashboard', 'profile', 'book_appointment', 'my_appointments'):
            self.assertEqual(self.client.get(reverse(route)).status_code, 200)
        for route in ('appointment_detail', 'edit_appointment', 'cancel_appointment'):
            self.assertEqual(self.client.get(reverse(route, args=[appointment.pk])).status_code, 200)

    def test_selected_doctor_is_prefilled(self):
        self.client.force_login(self.patient)
        response = self.client.get(reverse('book_appointment'), {'doctor': self.doctor.pk})
        self.assertEqual(str(response.context['form'].initial['doctor']), str(self.doctor.pk))
