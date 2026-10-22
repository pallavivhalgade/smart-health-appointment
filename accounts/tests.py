from unittest.mock import patch
from django.db import IntegrityError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from .forms import DoctorRegistrationForm, UserUpdateForm
from .models import DoctorProfile, User


class AccountTests(TestCase):
    def doctor_data(self):
        return {
            'username': 'newdoctor', 'first_name': 'Test', 'last_name': 'Doctor',
            'email': 'doctor@example.com', 'phone': '1234567890',
            'specialization': 'general_physician', 'license_number': 'TEST-LICENSE',
            'experience_years': 3, 'consultation_fee': 500,
            'password1': 'Example-pass-435!', 'password2': 'Example-pass-435!',
        }

    def test_duplicate_license_returns_validation_error(self):
        user = User.objects.create_user(username='existing', user_type='doctor')
        DoctorProfile.objects.create(user=user, specialization='general_physician', license_number='TEST-LICENSE')
        form = DoctorRegistrationForm(self.doctor_data())
        self.assertFalse(form.is_valid())
        self.assertIn('license_number', form.errors)
        self.assertFalse(User.objects.filter(username='newdoctor').exists())

    def test_failed_profile_creation_rolls_back_user(self):
        form = DoctorRegistrationForm(self.doctor_data())
        self.assertTrue(form.is_valid(), form.errors)
        with patch('accounts.forms.DoctorProfile.objects.create', side_effect=IntegrityError('profile error')):
            with self.assertRaises(IntegrityError):
                form.save()
        self.assertFalse(User.objects.filter(username='newdoctor').exists())

    def test_logout_requires_post(self):
        user = User.objects.create_user(username='patient')
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(self.client.post(reverse('logout')), reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_csrf_is_required_for_registration(self):
        response = Client(enforce_csrf_checks=True).post(reverse('register_doctor'), self.doctor_data())
        self.assertEqual(response.status_code, 403)

    @override_settings(ALLOW_PROFILE_UPLOADS=False)
    def test_serverless_profile_form_omits_local_file_upload(self):
        self.assertNotIn('profile_picture', UserUpdateForm().fields)


@override_settings(DEMO_MODE=True)
class DemoTests(TestCase):
    def test_public_pages_work_without_login(self):
        for route in ('home', 'doctor_list', 'symptom_checker', 'health'):
            with self.subTest(route=route):
                self.assertEqual(self.client.get(reverse(route)).status_code, 200)

    def test_accounts_and_admin_show_demo_notice(self):
        for route in ('login', 'register_patient', 'register_doctor', 'dashboard', 'profile', 'book_appointment', 'admin:index'):
            self.assertContains(self.client.get(reverse(route)), 'Browsing demo')

    def test_demo_rejects_account_writes(self):
        for route in ('login', 'register_patient', 'register_doctor', 'book_appointment'):
            self.assertEqual(self.client.post(reverse(route), {}).status_code, 405)
        self.assertEqual(User.objects.count(), 0)
