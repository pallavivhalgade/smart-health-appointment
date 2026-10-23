# SmartHealth Appointment Management System

A Django application for managing appointments between patients and doctors, with role-based dashboards and an educational symptom checker.

[Live browsing demo](https://smart-health-appointment-pi.vercel.app) · [Source code](https://github.com/pallavivhalgade/smart-health-appointment)

## Overview

Patients can register, browse doctors by specialization, book a time slot, and manage their appointments. Doctors can review requests, update appointment status, and add notes. Each account can access its own appointments and symptom history.

The symptom checker matches text against a local keyword dataset to suggest a specialty. It is not an AI diagnostic model or a substitute for medical care. Doctor self-registration does not verify professional credentials.

## Technology Stack

- Python 3.12 and Django 5.2 LTS
- SQLite for local development; PostgreSQL for writable cloud deployments
- Django templates, Bootstrap, and shared CSS
- Vercel, with Gunicorn and WhiteNoise available for other hosts
- Django tests and GitHub Actions

## Core Features

- Patient and doctor registration, authentication, and profile management
- Public doctor directory with specialization filters
- Booking, editing, cancellation, and doctor status updates
- Validation for unavailable doctors, elapsed slots, and a 30-day booking window
- Database protection against duplicate active bookings; cancelled slots can be booked again
- Keyword-based specialty suggestions and private history for signed-in users
- A read-only browsing demo with fictional profiles

## Project Structure

```text
accounts/           Users, profiles, registration, dashboards, and demo seed command
appointments/       Scheduling models, forms, availability rules, and views
symptom_checker/    Keyword dataset, analyzer, views, and history
smarthealth/        Django settings, URLs, middleware, and health endpoint
templates/          Shared layout and demo notice
static/css/         Shared site styles
scripts/            Vercel build preparation
docs/               Deployment instructions
.github/workflows/  Automated validation
```

Virtual environments, database files, uploads, bytecode, secrets, and build output are excluded from version control. Previously tracked copies are removed from the current tree; Git history is unchanged.

## Run Locally

```sh
git clone https://github.com/pallavivhalgade/smart-health-appointment.git
cd smart-health-appointment
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```sh
source .venv/bin/activate
```

Copy `.env.example` to `.env`, then install dependencies and initialize an empty local database:

```sh
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. Register a doctor and patient to try the booking workflow. For administration, run `python manage.py createsuperuser` and visit `/admin/`.

The development server serves static assets automatically. If PowerShell prevents activation, run commands directly with `.\.venv\Scripts\python.exe`.

## Validation

```sh
python manage.py collectstatic --noinput
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Tests cover cancelled-slot reuse, duplicate active bookings, date limits, elapsed slots, authorization, registration rollback, CSRF, logout, demo write restrictions, and symptom-history isolation. GitHub Actions runs these checks on pushes and pull requests.

## Deployment

See [deployment instructions](docs/deployment.md) for Vercel environment variables, PostgreSQL setup, and alternative hosting.

| Mode | Storage | Available workflows |
| --- | --- | --- |
| Local development | Local SQLite | Full application |
| Vercel browsing demo | Generated read-only SQLite with fictional profiles | Directory, specialty filters, example symptom checks |
| Full cloud application | External PostgreSQL | Accounts and persistent appointments; profile uploads require object storage |

Vercel deployments default to the browsing demo when no `DATABASE_URL` is configured. Account and appointment writes are disabled in that mode. Persistent booking requires PostgreSQL; an ephemeral SQLite database would lose changes between function instances.

## Author

Pallavi Vijay Vholgade

B.E. Artificial Intelligence & Machine Learning

---

## About the developer

Built by **Pallavi Vholgade**. Explore my AI / ML projects, experience, and skills in my [portfolio](https://pallavi-portfolio-preview.vercel.app).

[LinkedIn](https://www.linkedin.com/in/pallavi-vholgade-05565b24b) · [Email](mailto:pallavivhalgade@gmail.com)
