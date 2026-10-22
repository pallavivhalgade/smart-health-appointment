"""Prepare an isolated demo DB, or migrate an explicitly configured database."""
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarthealth.settings')
os.environ['SMARTHEALTH_BUILD_DEMO'] = '1'

import django
django.setup()

from django.conf import settings
from django.core.management import call_command

if settings.DEMO_MODE:
    call_command('migrate', interactive=False, verbosity=0)
    call_command('seed_demo')
elif os.environ.get('DATABASE_URL'):
    call_command('migrate', interactive=False)
else:
    raise RuntimeError('Set DATABASE_URL or enable DJANGO_DEMO_MODE before deploying.')
