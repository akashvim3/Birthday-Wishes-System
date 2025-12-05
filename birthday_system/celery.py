import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'birthday_system.settings')

# Create Celery app
app = Celery('birthday_system')

# Load configuration from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'check-birthdays-daily': {
        'task': 'wishes.tasks.check_birthdays_today',
        'schedule': crontab(hour=0, minute=0),  # Run at midnight daily
    },
    'send-birthday-reminders': {
        'task': 'wishes.tasks.send_birthday_reminders',
        'schedule': crontab(hour=8, minute=0),  # Run at 8 AM daily
    },
    'cleanup-old-voice-messages': {
        'task': 'wishes.tasks.cleanup_old_voice_messages',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Weekly on Sunday at 2 AM
    },
}

# Celery configuration
app.conf.update(
    result_expires=3600,
    task_always_eager=False,
    task_eager_propagates=False,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing"""
    print(f'Request: {self.request!r}')
