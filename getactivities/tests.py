from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from dateutil.relativedelta import relativedelta

from .models import FetchActivitiesTask
from .tasks import fetchactivities_task

from allauth.socialaccount.models import SocialApp, SocialToken, SocialAccount
# Create your tests here.

STRAVA_API = settings.STRAVA_API

class GetactivitiesTest(TestCase):

    def setUp(self):
        u = User.objects.create(username="lgalarneau")
        u.save()

        FetchActivitiesTask.objects.create(
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
            client_id='65506',
            secret='8d127df0e3426ce186314d064d3206bac8c2bed8',
            key='23df88df854fb2bbf460d4415f85a9d49a099451',
        )
        sap.save()

        ta = SocialToken.objects.create(
            app=sap,
            account=sa,
            token_secret='9a9f6fd4085f126a4e8bc0aafcb634610d1485d9'
        )
        ta.save()


    def test_date_delta(self):
        u = User.objects.get(username="lgalarneau")
        gettask, created = FetchActivitiesTask.objects.get_or_create(user=u)
        self.assertFalse(created)

        sa = SocialAccount.objects.get(user=u)
        self.assertEqual(sa.user, u)

        sap = SocialApp.objects.get(name=STRAVA_API['name'])
        self.assertEqual(sap.name, 'lgactivities')

        ta = SocialToken.objects.get(app=sap)
        self.assertEqual(ta.app, sap)

        gat = fetchactivities_task(user=u)
        self.assertTrue(gat)

# class GetTaskTest(TestCase):
#
#     def setUp(self):
#         u = User.objects.create(username="lgalarneau")
#         u.save()
#
#     def test_date_delta(self):
#         u = User.objects.get(username="lgalarneau")