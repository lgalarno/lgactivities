from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.conf import settings
from dateutil.relativedelta import relativedelta

from .models import SyncActivitiesTask
from .tasks import get_activities_task

from allauth.socialaccount.models import SocialApp, SocialToken, SocialAccount
# Create your tests here.

STRAVA_API = settings.STRAVA_API
STRAVA_CLIENT_ID = settings.STRAVA_CLIENT_ID
STRAVA_CLIENT_SECRET = settings.STRAVA_CLIENT_SECRET


class GetactivitiesTest(TestCase):

    def setUp(self):
        u = User.objects.create(username="lgalarneau")
        u.save()

        SyncActivitiesTask.objects.create(
            user=u,
            start_date="2021-08-17T02:35:14Z",
            end_date="2021-08-21T02:35:14Z",
            active=True,
            frequency=1
            )

        sa = SocialAccount.objects.create(
            user=u,
            provider="Strava",
            uid='1490709'
        )

        sap = SocialApp.objects.create(
            provider="Strava",
            name='lgactivities',
            client_id=STRAVA_CLIENT_ID,
            secret=STRAVA_CLIENT_SECRET,
            key='',
        )
        sap.save()

        ta = SocialToken.objects.create(
            app=sap,
            account=sa,
            token_secret=''
        )
        ta.save()

    def test_date_delta(self):
        u = User.objects.get(username="lgalarneau")
        gettask, created = SyncActivitiesTask.objects.get_or_create(user=u)
        self.assertFalse(created)

        sa = SocialAccount.objects.get(user=u)
        self.assertEqual(sa.user, u)

        sap = SocialApp.objects.get(name=STRAVA_API['name'])
        self.assertEqual(sap.name, 'lgactivities')

        ta = SocialToken.objects.get(app=sap)
        self.assertEqual(ta.app, sap)

        gati = get_activities_task(user=u.id, get_type="import")
        self.assertTrue(gati)

        gats = get_activities_task(user=u.id, get_type="sync")
        self.assertTrue(gats)


# class GetTaskTest(TestCase):
#
#     def setUp(self):
#         u = User.objects.create(username="lgalarneau")
#         u.save()
#
#     def test_date_delta(self):
#         u = User.objects.get(username="lgalarneau")


