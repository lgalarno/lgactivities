from django.contrib.auth.models import User
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from django.db import models
from django.dispatch import receiver

from allauth.socialaccount.models import SocialAccount
from allauth.account.signals import user_signed_up, user_logged_in

from urllib.request import urlopen

import os

# Create your models here.


def upload_location(instance, filename):
    return f"avatars/{instance}/{filename}"


#TODO store username from Strava with signals?
#TODO add extra data from Strava?
#TODO save avatar locally
class StravaProfile(models.Model):
    user        = models.OneToOneField(User, related_name="strava_profile", on_delete=models.CASCADE)
    city        = models.CharField(max_length=120, blank=True, null=True)
    country     = models.CharField(max_length=120, blank=True, null=True)
    avatar_url  = models.URLField(max_length=200, blank=True, null=True)
    avatar      = models.ImageField(upload_to=upload_location, null=True, blank=True)

    def __str__(self):
        return self.user.username

    def get_avatar_from_url(self, url=None):
        img_tmp = NamedTemporaryFile(delete=True)
        if url is None:
            url = self.avatar_url
        if url is not None:
            with urlopen(url) as uo:
                assert uo.status == 200
                img_tmp.write(uo.read())
                img_tmp.flush()
            img = File(img_tmp)
            self.avatar.save(f"avatar.jpg", img)


@receiver(user_signed_up)
def retrieve_social_data(request, user, **kwargs):
    """Get extra data from sociallogin when signed_up and put it into StravaProfile."""
    # in this signal I can retrieve the obj from SocialAccount
    sa = SocialAccount.objects.get(user=user)
    # check if the user has signed up via social media
    if sa:
        avatar_url = sa.get_avatar_url()
        profile, created = StravaProfile.objects.get_or_create(user=user)
        profile.avatar_url = avatar_url
        # profile.avatar = get_avatar_from_url(avatar_url)
        profile.get_avatar_from_url(avatar_url)
        profile.city = sa.extra_data.get("city")
        profile.country = sa.extra_data.get("country")
        profile.save()
        username = sa.extra_data.get("username")
        if (not username == "") and (not username==None):
            u = User.objects.get(pk=user.pk)
            u.username = username
            u.save()


#TODO update StravaProfile
@receiver(user_logged_in)
def update_social_data(request, user, **kwargs):
    sa, created = StravaProfile.objects.get_or_create(user=user)
    if created:
        retrieve_social_data(request, user, **kwargs)


@receiver(models.signals.post_delete, sender=StravaProfile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `StravaProfile` object is deleted.
    """
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)


@receiver(models.signals.pre_save, sender=StravaProfile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `StravaProfile` object is updated
    with new file.
    """
    if not instance.pk:
        return False
    try:
        old_avatar = StravaProfile.objects.get(pk=instance.pk).avatar
    except StravaProfile.DoesNotExist:
        return False
# TODO make it better...
    new_avatar = instance.avatar
    if not bool(old_avatar):
        return False
    if not old_avatar == new_avatar:
        if os.path.isfile(old_avatar.path):
            os.remove(old_avatar.path)
