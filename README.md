# PhilHealth eKonsulta System

A PhilHealth eKonsulta management system developed as an On-the-Job Training (OJT) project.

## About

This project is a comprehensive healthcare management system designed to streamline PhilHealth-related processes including patient management, doctor consultations, appointment scheduling, and billing/payment processing.

## Features

### User Roles
- **Superadmin** - System administration and user management
- **Secretary** - Patient registration and appointment scheduling
- **Doctor** - Patient consultations and prescriptions
- **Finance** - Billing and payment processing

### Secretary Module
- Patient registration with medical history
- Document and picture uploads for patients
- Appointment scheduling with doctors

### Doctor Module
- View and manage appointments
- Patient consultation with diagnosis
- Prescription system with searchable medicine dropdown (Select2)
- Reason notes and additional notes
- My Patients - view patients with approved/completed appointments

### Finance Module
- Billing dashboard for completed consultations
- Patient billing details with itemized medicines
- Cash payment processing
- PhilHealth coverage application
- Transaction history tracking

### Other Features
- Landing page with User/Admin login options
- Role-based dashboard navigation
- Dark/Light mode support (Superadmin)
- Custom management command for medicine data (`py manage.py get_medlist`)
- Custom management command for medicine data (`py manage.py create_superuser`)
- Custom management command for medicine data (`py manage.py create_dummy_acc`)

## Tech Stack

- **Backend**: Django 6.0 (Python)
- **Frontend**: Bootstrap 5, Select2
- **Database**: PostgreSQL
- **Authentication**: Django built-in auth with custom user model

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL
- Docker (optional, for database)

### Installation

```bash
# Clone the repository
git clone https://github.com/SkieAdmin/PHILHEALTH_SYS_OJT.git

# Navigate to project directory
cd PHILHEALTH_SYS_OJT/philhealth_eKonsulta

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install django psycopg2-binary pillow

# Run migrations
python manage.py migrate

# Load medicine data
python manage.py get_medlist

# Create superuser
python manage.py createsuperuser
```

### Running the Project

```bash
# Start development server
python manage.py runserver 8011

# Access the application
# Landing Page: http://localhost:8011/
# Admin Login: http://localhost:8011/superadmin-login/
# User Login: http://localhost:8011/login/
# Django Admin: http://localhost:8011/admin/
```

## Project Structure

```
PHILHEALTH_SYS_OJT/
├── philhealth_eKonsulta/
│   ├── doctor/              # Doctor app (consultations, prescriptions)
│   ├── finance/             # Finance app (billing, payments)
│   ├── login/               # Auth app (users, profiles, templates)
│   ├── secretary/           # Secretary app (patients, appointments)
│   ├── philhealth_eKonsulta/ # Project settings
│   └── manage.py
├── README.md
└── ...
```

## Database Configuration

Edit `philhealth_eKonsulta/settings.py` and set `DATABASE_MODE`:
- `"Docker"` - PostgreSQL via Docker (port 9095)
- `"Live"` - Remote PostgreSQL server
- `"Sol"` - Local Windows PostgreSQL

## Contributing

This is an OJT project. Contributions and feedback are welcome.

## Team Roles & Contributions

- **Rhod Celister Sol** – Web Architecture / Backend Developer  
  - Built the system foundation  
  - Implemented core features  
  - Designed initial data models  

- **Kerneil Rommel S. Gocotano** – System Architecture / Backend Developer  
  - Added new features  
  - Improved existing features  
  - Refined and add & optimized system models  

- **Michael Vincent Rendado** – Web Developer  
  - Integrated frontend with backend  


## License

*This Project is well.... NOT LICENSED, THIS PROJECT is Under IT Company (Eversoft IT Solution) for our OJT Project.*

---

**OJT Project** | PhilHealth eKonsulta System
