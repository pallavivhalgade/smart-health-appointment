# SmartHealth Appointment Management System

A backend-focused healthcare appointment management web application built using Django, designed to support structured workflows, data validation, and production-ready deployment.

🔗 Live Demo: [View Application][live-demo]  
📂 Source Code: [View Repository][source-code]

---

## Overview

SmartHealth is a role-based appointment management system that enables secure scheduling between patients and doctors.  
The application emphasizes backend engineering, database integrity, and deployment readiness rather than UI complexity.

---

## Technology Stack

- Backend: Python, Django  
- Database: SQLite  
- Frontend: Django Templates, HTML, CSS  
- Deployment: Render, Gunicorn, WhiteNoise  
- Version Control: Git, GitHub  

---

## Core Features

- Role-based authentication (Admin / Doctor / Patient)
- Appointment scheduling and management
- Backend data validation and consistency checks
- Secure authentication and authorization workflows
- Production-ready static file handling

---

## Engineering Practices

- Modular Django app architecture
- Data preprocessing and validation
- Unit testing and debugging
- Technical documentation
- Cloud deployment using WSGI server

---

## Deployment

- Hosted on cloud infrastructure
- Served using Gunicorn WSGI server
- Static assets managed with WhiteNoise
- Dependency management via `requirements.txt`

---

## How to Clone and Run Locally

### Clone the Repository
```bash
git clone [source-code]
cd smart-health-appointment
Create and Activate Virtual Environment
python -m venv env
env\Scripts\activate

### Install Dependencies
pip install -r requirements.txt

### Apply Migrations and Run
python manage.py migrate
python manage.py collectstatic
python manage.py runserver


### Author

Pallavi Vijay Vholgade
B.E. Artificial Intelligence & Machine Learning



---

