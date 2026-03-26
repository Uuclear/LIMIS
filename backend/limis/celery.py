import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limis.settings')

app = Celery('limis')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'equipment-calibration-check': {
        'task': 'apps.equipment.tasks.check_calibration_expiry',
        'schedule': crontab(hour=8, minute=0),
    },
    'staff-age-reminder': {
        'task': 'apps.staff.tasks.send_age_reminders',
        'schedule': crontab(hour=9, minute=0),
    },
    'environment-data-check': {
        'task': 'apps.environment.tasks.check_environment_data',
        'schedule': 300.0,
    },
}
