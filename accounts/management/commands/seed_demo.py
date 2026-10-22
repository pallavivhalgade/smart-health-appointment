from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from accounts.models import DoctorProfile, User


class Command(BaseCommand):
    help = 'Create fictional doctors for the read-only demo. No login credentials.'

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEMO_MODE:
            raise CommandError('seed_demo is only available with DJANGO_DEMO_MODE=true.')
        for number, (first, last, specialty) in enumerate([
            ('Avery', 'Demo', 'general_physician'),
            ('Jordan', 'Sample', 'cardiologist'),
            ('Morgan', 'Example', 'dermatologist'),
            ('Taylor', 'Demo', 'pediatrician'),
            ('Casey', 'Sample', 'orthopedic'),
            ('Riley', 'Example', 'ent'),
        ], start=1):
            user, _ = User.objects.get_or_create(username=f'demo-doctor-{number}', defaults={
                'first_name': first, 'last_name': last, 'user_type': 'doctor', 'is_active': False,
            })
            user.set_unusable_password()
            user.save(update_fields=['password'])
            DoctorProfile.objects.get_or_create(user=user, defaults={
                'specialization': specialty, 'license_number': f'FICTIONAL-{number}',
                'experience_years': number + 4, 'consultation_fee': 500,
                'bio': 'Fictional profile for demonstrating the SmartHealth directory.',
            })
        self.stdout.write(self.style.SUCCESS('Fictional demo directory ready.'))
