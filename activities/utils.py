from django.conf import settings

import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from getactivities.utils import formaterror, get_token

# from .models import Map

STRAVA_API = settings.STRAVA_API

def send_email(to_email, mail_subject, mail_body):
    username = settings.FROM_EMAIL
    password = settings.EMAIL_PASSWORD

    mimemsg = MIMEMultipart()
    mimemsg['From']=username
    mimemsg['To'] = to_email
    mimemsg['Subject']=mail_subject
    mimemsg.attach(MIMEText(mail_body, 'plain'))
    try:
        connection = smtplib.SMTP(host='smtp.office365.com', port=587)
        connection.starttls()
        connection.login(username,password)
        connection.send_message(mimemsg)
        connection.quit()
        return True
    except Exception as e:
        connection.quit()
        return e


def update_segment(u, this_effort):
    e, access_token = get_token(user=u)
    if not e:
        header = {'Authorization': f'Bearer {access_token}'}
        param = {}
        url = f"{STRAVA_API['URLS']['athlete']}segments/{this_effort.segment_id}"
        segment_detail = requests.get(url, headers=header, params=param, verify=False).json()
        if 'errors' in segment_detail:
            e = formaterror(segment_detail['errors'])
            return e
            # e = formaterror(segment_detail['errors'])
            # messages.warning(request, f'An error occurred while getting the segment: {e}')
            # return HttpResponseRedirect('/')
        else:
            this_effort.segment.update_from_strava(segment_detail=segment_detail)
            return True
