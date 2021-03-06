from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.shortcuts import reverse

import datetime


class ActivityType(models.Model):
    name = models.CharField(max_length=127)
    icon = models.CharField(max_length=127, blank=True, null=True)
    color = models.CharField(max_length=31, blank=True, null=True)

    def __str__(self):
        return self.name


class Activity(models.Model):
    id = models.BigIntegerField(primary_key=True)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    type = models.ForeignKey(to=ActivityType,
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    start_date_local = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Activities"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('activities:activity-details', args=(self.id,))

    def get_all_segments(self):
        return self.segmenteffort_set.all()

    def get_date(self, *args, **kwargs):
        return self.start_date_local.strftime("%m/%d/%Y")

    @property
    def get_html_url(self):
        url = reverse('activities:activity-details', args=(self.id,))
        return f'<a href="{url}"> {self.name} </a>'

    @property
    def get_strava_url(self):
        return f'https://www.strava.com/activities/{self.id}'

#
# @receiver(models.signals.pre_save, sender=Activity)
# def get_type_icon(sender, instance, **kwargs):
#     """
#     Task to send an e-mail notification when a new activity type is created.
#     And administrator will have to update ACTIVITY_ICONS accordingly
#     """
#     type = instance.type
#     if type == "" or type is None:
#         pass
#     else:
#         i = ACTIVITY_ICONS.get(type)
#         if i is not None:
#             instance.icon = icon_path + i
#         else:
#             mail_subject = 'lgactivities - New activity type'
#             mail_body = f"""
#             A new activity type was entered into the database of lgactivities and will require a new icon:
#
#             Activity type: {type}
#             Activity ID: {instance.id}
#             user: {instance.user}
#
#             This email was sent by lgactivities.
#             """
#             send_email.delay(to_email='lgalarno@outlook.com', mail_subject=mail_subject, mail_body=mail_body)
#             instance.icon = ""
#             # instance.icon = 'email'


# https://www.strava.com/activities/5249323025/segments/2825228422414629460
class Segment(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)
    kom = models.CharField(max_length=20, blank=True, null=True)
    qom = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

    def update_from_strava(self, segment_detail):
        self.kom = segment_detail.get('xoms').get('kom')
        self.qom = segment_detail.get('xoms').get('qom')
        self.updated = segment_detail.get('updated_at')
        self.save()
        m, created = Map.objects.get_or_create(segment=self)
        if created:
            m.polyline = segment_detail.get('map').get('polyline')
            m.save()
        return self

    def get_all_efforts(self, user=None):
        return self.segmenteffort_set.filter(activity__user=user)

    def get_stared(self, user=None):
        return self.staredsegment_set.filter(user=user)

    def is_stared(self, user=None):
        if len(self.staredsegment_set.filter(user=user)) > 0:
            return True
        else:
            return False

    @property
    def get_staring_api_url(self):
        return reverse('activities:activities-api:SegmentStaringAPIToggle', kwargs={"segment_id": self.id})

    @property
    def get_plotdata_api_url(self):
        return reverse('activities:activities-api:SegmentDataAPI', kwargs={"segment_id": self.id})


class StaredSegment(models.Model):
    segment = models.ForeignKey(to=Segment, on_delete=models.CASCADE)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.segment.name}"

    def get_number_efforts(self):
        return self.segment.segmenteffort_set.filter(activity__user=self.user).count()

    def get_best_effort(self):
        return self.segment.segmenteffort_set.filter(activity__user=self.user).order_by('elapsed_time').first()

    def get_last_effort(self):
        return self.segment.segmenteffort_set.filter(activity__user=self.user).order_by('-start_date_local').first()

    def get_best_effort_url(self):
        best = self.get_best_effort()
        return reverse('activities:effort_details', kwargs={'pk': best.pk})

    def get_type(self):
        se = self.segment.segmenteffort_set.filter(activity__user=self.user).first()
        return se.activity.type


class Map(models.Model):
    activity = models.OneToOneField(to=Activity,
                                    on_delete=models.CASCADE,
                                    blank=True,
                                    null=True)
    segment = models.OneToOneField(to=Segment,
                                   on_delete=models.CASCADE,
                                   blank=True,
                                   null=True)
    polyline = models.TextField(blank=True, null=True)

    @property
    def get_mapdata_api_url(self):
        return reverse('activities:activities-api:GetMapDataAPI', kwargs={"model_id": self.id})

    def __str__(self):
        if self.activity:
            return f'Activity: {self.activity.name}'
        elif self.segment:
            return f'Segment: {self.segment.name}'


class SegmentEffort(models.Model):
    id = models.BigIntegerField(primary_key=True)
    activity = models.ForeignKey(to=Activity,
                                 on_delete=models.CASCADE)
    elapsed_time = models.IntegerField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    start_date_local = models.DateTimeField(blank=True, null=True)
    distance = models.FloatField(blank=True, null=True)
    pr_rank = models.IntegerField(blank=True,
                                  null=True)  # The rank of the effort on the athlete's leaderboard if it belongs in the top 3 at the time of upload
    segment = models.ForeignKey(to=Segment,
                                null=True,
                                blank=True,
                                on_delete=models.CASCADE)

    class Meta:
        ordering = ['start_date_local']

    def __str__(self):
        return f"{self.activity.name}: {self.segment.name}"

    def get_time(self, *args, **kwargs):
        return str(datetime.timedelta(seconds=self.elapsed_time))

    def get_date(self, *args, **kwargs):
        return self.start_date_local.strftime("%m/%d/%Y")

    @property
    def get_strava_url(self):
        return f'https://www.strava.com/activities/{self.activity_id}/segments/{self.id}'


@receiver(models.signals.pre_save, sender=SegmentEffort)
def set_pr_rank(sender, instance, **kwargs):
    if instance.id is None:
        pass
    else:
        s = Segment.objects.get(id=instance.segment.id)
        pr = 1
        sefforts = s.segmenteffort_set.all().order_by('elapsed_time')[:3]
        for se in sefforts:
            if instance.elapsed_time < se.elapsed_time:
                break
            pr += 1
        if pr > 3:
            instance.pr_rank = None
        else:
            instance.pr_rank = pr
