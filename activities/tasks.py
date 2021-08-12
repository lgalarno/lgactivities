from celery import shared_task
from django.conf import settings

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


STRAVA_API = settings.STRAVA_API

@shared_task
def send_email(to_email, mail_subject, mail_body):
    username = settings.FROM_EMAIL
    password = settings.EMAIL_PASSWORD

    mimemsg = MIMEMultipart()
    mimemsg['From']=username
    mimemsg['To'] = to_email
    mimemsg['Subject']=mail_subject
    mimemsg.attach(MIMEText(mail_body, 'plain'))
    print('email1')
    try:
        print('email2')
        connection = smtplib.SMTP(host='smtp.office365.com', port=587)
        connection.starttls()
        connection.login(username,password)
        connection.send_message(mimemsg)
        connection.quit()
        print('email3')
        return True
    except Exception as e:
        connection.quit()
        return e