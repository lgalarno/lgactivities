from django.db import models

from allauth.socialaccount.models import SocialApp

# Create your models here.


# class Token(models.Model):
#     app             = models.OneToOneField(to=SocialApp,
#                                            on_delete=models.CASCADE,
#                                            primary_key=True)
#     code            = models.CharField(max_length=40, blank=True, null=True)
#     access_token    = models.CharField(max_length=40, blank=True, null=True)
#     refresh_token   = models.CharField(max_length=40, blank=True, null=True)
#     scope           = models.CharField(max_length=120, blank=True, null=True)
#     token_type      = models.CharField(max_length=120, blank=True, null=True)
#     expires_at      = models.IntegerField(blank=True, null=True, default=0)
#     expires_in      = models.IntegerField(blank=True, null=True, default=0)
#
#     def __str__(self):
#         return self.app.name
