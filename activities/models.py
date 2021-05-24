from django.db import models
from django.shortcuts import reverse

import datetime


# Create your models here.


class Activity(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=127)
    start_lat = models.FloatField(blank=True, null=True)
    start_lng = models.FloatField(blank=True, null=True)
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

    @property
    def get_center(self):
        return [self.start_lat, self.start_lng]

    @property
    def get_html_url(self):
        url = reverse('activities:activity-details', args=(self.id,))
        return f'<a href="{url}"> {self.name} </a>'

    @property
    def get_strava_url(self):
        return f'https://www.strava.com/activities/{self.id}'


# https://www.strava.com/activities/5249323025/segments/2825228422414629460

class Segment(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    staring = models.BooleanField(default=False, blank=True)
    start_lat = models.FloatField(blank=True, null=True)
    start_lng = models.FloatField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)
    kom = models.CharField(max_length=20, blank=True, null=True)
    qom = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('activities:segment_details', args=(self.id,))

    def get_all_efforts(self):
        return self.segmenteffort_set.all()

    @property
    def get_center(self):
        return [self.start_lat, self.start_lng]

    @property
    def get_staring_api_url(self):
        return reverse('activities:SegmentStaringAPIToggle', kwargs={"segment_id": self.id})

    @property
    def has_map(self):
        try:
            self.map
            return True
        except:
            return False


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

    # segment_efforts

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

    def __str__(self):
        return f"{self.activity.name}: {self.segment.name}"

    def get_time(self, *args, **kwargs):
        return str(datetime.timedelta(seconds=self.elapsed_time))

    def save(self, *args, **kwargs):
        s = Segment.objects.get(id=self.segment.id)
        pr = 1
        sefforts = s.segmenteffort_set.all().order_by('elapsed_time')[:3]
        for se in sefforts:
            if self.elapsed_time < se.elapsed_time:
                break
            pr += 1
        if pr > 3:
            self.pr_rank = None
        else:
            self.pr_rank = pr
        super(SegmentEffort, self).save(*args, **kwargs)

    @property
    def get_strava_url(self):
        return f'https://www.strava.com/activities/{self.activity_id}/segments/{self.id}'
