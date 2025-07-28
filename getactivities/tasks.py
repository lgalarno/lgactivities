from django.conf import settings
from django.contrib.auth import get_user_model

from celery import shared_task
from dateutil.relativedelta import relativedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import getactivities.utils as utils
from .models import ImportActivitiesTask, SyncActivitiesTask

import smtplib


User = get_user_model()
STRAVA_API = settings.STRAVA_API


@shared_task
def send_email(to_email, mail_subject, mail_body):
    username = settings.FROM_EMAIL
    password = settings.EMAIL_PASSWORD
    mimemsg = MIMEMultipart()
    mimemsg['From'] = username
    mimemsg['To'] = to_email
    mimemsg['Subject'] = mail_subject
    mimemsg.attach(MIMEText(mail_body, 'plain'))
    try:
        with smtplib.SMTP('smtp.mail.yahoo.com', 587) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(mimemsg)
        return True
    except Exception as e:
        return e


def _update_task_model(model=None):
    # today = datetime.utcnow().replace(tzinfo=pytz.utc)
    if model.frequency > 7:
        from_date = model.from_date + relativedelta(months=1)
        model.to_date = from_date + relativedelta(months=1)
    else:
        from_date = model.from_date + relativedelta(days=model.frequency)
        model.to_date = from_date + relativedelta(days=model.frequency)
    model.from_date = from_date
    model.save()


@shared_task
def get_activities_task(user=None, get_type=None):
    try:
        u = User.objects.get(pk=user)
        if get_type == 'import':
            get_task_model = ImportActivitiesTask.objects.get(user=u)
            get_task_model.n_intervals -= 1
        elif get_type == 'sync':
            get_task_model = SyncActivitiesTask.objects.get(user=u)
        else:
            return f"ERROR! User {user} task type does not exist."
        g = utils.get_activities(user=u, start_date=get_task_model.from_date, end_date=get_task_model.to_date)
        _update_task_model(get_task_model)
        return g
    except ImportActivitiesTask.DoesNotExist:
        return f"ERROR! User {user} task does not exist."
