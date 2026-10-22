from django.test import TestCase, override_settings
from django.urls import reverse
from accounts.models import User
from .models import SymptomCheck


class SymptomCheckerTests(TestCase):
    @override_settings(DEMO_MODE=True)
    def test_demo_analysis_does_not_store_input(self):
        response = self.client.post(reverse('symptom_checker'), {'symptoms': 'headache and dizziness'})
        self.assertContains(response, 'Analysis Results')
        self.assertEqual(SymptomCheck.objects.count(), 0)

    def test_oversized_input_is_rejected(self):
        response = self.client.post(reverse('symptom_checker'), {'symptoms': 'x' * 2001})
        self.assertContains(response, 'under 2,000 characters')
        self.assertIsNone(response.context['result'])

    def test_authenticated_check_has_private_history(self):
        owner = User.objects.create_user(username='owner')
        other = User.objects.create_user(username='other')
        self.client.force_login(owner)
        self.client.post(reverse('symptom_checker'), {'symptoms': 'headache'})
        self.assertEqual(SymptomCheck.objects.get().user, owner)
        self.client.force_login(other)
        self.assertEqual(list(self.client.get(reverse('symptom_history')).context['checks']), [])
