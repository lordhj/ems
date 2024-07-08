# Project Name

A comprehensive event management system - where users can create and
manage events. The system support user roles (organizers and participants), event
scheduling, ticket booking, notifications, and basic analytics.


## Prerequisites

- Python 3.9 +
- Pip (Python package installer)

## Getting Started

### 1. Clone the repository

git clone https://github.com/lordhj/ems.git
cd ems/

### 2 . Create and activate a virtual environment (optional but recommended)

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate

# Install Requirements
pip install -r requirements.txt


### 3. Apply database migrations
python manage.py migrate


### 4. Run the development server
python manage.py runserver

### 5. Setup celery and redis as per your system
You can either run celery or use some dameon

celery -A ems worker --loglevel=info


Also set the email credentials in settings.py


### 6. Access the application
Open your web browser and go to http://localhost:8000/ to access the application.

