# 🎉 Birthday Wishes Pro - Professional Django Application

A comprehensive, production-ready Django application for managing birthday wishes with advanced features including voice messages, AI-powered chatbot, group wishes, gift suggestions, and calendar integration.

## ✨ Features

- 🎂 **Smart Birthday Management** - Never miss a birthday with automated reminders
- 🎙️ **Voice Messages** - Record and send personalized voice birthday wishes
- 🤖 **AI Chatbot Assistant** - Get help creating perfect birthday messages
- 👥 **Group Wishes** - Collaborate with friends for memorable group celebrations
- 🎁 **Gift Suggestions** - Curated gift ideas based on preferences
- 📅 **Calendar Integration** - Full calendar view with Google Calendar sync
- ⏰ **Smart Scheduling** - Schedule wishes in advance
- 📱 **Responsive Design** - Beautiful UI that works on all devices
- 🔔 **Real-time Notifications** - Stay updated with Celery-powered notifications

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose (optional)

### Installation

1. **Clone the repository**

       git clone https://github.com/akashvim3/birthday-wishes-system.git
       cd birthday-wishes-system

2. **Create virtual environment**

       python -m venv venv
       source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies**

       pip install -r requirements.txt

4. **Set up environment variables**

       cp .env.example .env
       Edit .env with your configuration

5. **Run migrations**

       python manage.py migrate

6. **Create superuser**
              
       python manage.py createsuperuser

7. **Collect static files**

       python manage.py collectstatic

8. **Run development server**

       python manage.py runserver

Visit `http://localhost:8000` to see the application.

### Using Docker

Build and start all services
docker-compose up --build
Access the application at http://localhost

## 📋 Running Celery

For automated birthday reminders and scheduled tasks:
Start Celery worker
celery -A birthday_system 
worker -l info
Start Celery beat (scheduler)
celery -A birthday_system 
beat -l info

## 🏗️ Project Structure

    birthday_wishes_system/
    ├── birthday_system/       # Project configuration
    │   ├── settings.py
    │   ├── urls.py
    │   ├── celery.py
    │   └── wsgi.py
    ├── wishes/               # Main application
    │   ├── models.py        # Database models
    │   ├── views.py         # View logic
    │   ├── forms.py         # Form definitions
    │   ├── tasks.py         # Celery tasks
    │   ├── admin.py         # Admin customization
    │   └── templates/       # HTML templates
    ├── static/              # Static files (CSS, JS, images)
    ├── media/               # User uploads
    ├── requirements.txt     # Python dependencies
    ├── Dockerfile
    ├── docker-compose.yml
    └── README.md

## 🔧 Configuration

### Database Setup (PostgreSQL)

CREATE DATABASE birthday_wishes_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE birthday_wishes_db TO postgres;

### Email Configuration

Update `.env` with your SMTP settings:
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

## 🌐 Production Deployment

### Using Gunicorn + Nginx

1. Install Gunicorn

       pip install gunicorn

2. Run Gunicorn birthday_system

wsgi:application --bind 0.0.0.0:8000 --workers 4

1. Configure Nginx (see `nginx.conf`)

### Using Docker

    docker-compose -f docker-compose.yml up -d

## 📱 API Endpoints

- `/` - Homepage
- `/dashboard/` - User dashboard
- `/create-wish/` - Create birthday wish
- `/calendar/` - Birthday calendar
- `/gifts/` - Gift suggestions
- `/group-wishes/` - Group wishes management
- `/profile/` - User profile
- `/api/chatbot/` - Chatbot API

## 🧪 Testing

    python manage.py test

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Created with ❤️ by Akash

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For support, email support@birthdaywishpro.com

---

Made with 💜 using Django
