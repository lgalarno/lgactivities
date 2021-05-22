from django.db import models

# Create your models here.

class StravaApp(models.Model):
    name            = models.CharField(max_length=120)
    category        = models.CharField(max_length=120, blank=True, null=True)
    club            = models.CharField(max_length=120, blank=True, null=True)
    website         = models.CharField(max_length=120, blank=True, null=True)
    description     = models.TextField(blank=True, null=True)
    callback_domain = models.CharField(max_length=120)
    client_id 	    = models.CharField(max_length=5)
    client_secret   = models.CharField(max_length=40)
    # access_token    = models.CharField(max_length=40)
    refresh_token   = models.CharField(max_length=40)
    # code            = models.CharField(max_length=40)
    # grant_type      = models.CharField(max_length=120)

    def __str__(self):
        return self.name

class Token(models.Model):
    app             = models.OneToOneField(to=StravaApp,
                                           on_delete=models.CASCADE,
                                           primary_key=True)
    code            = models.CharField(max_length=40, blank=True, null=True)
    access_token    = models.CharField(max_length=40, blank=True, null=True)
    refresh_token   = models.CharField(max_length=40, blank=True, null=True)
    scope           = models.CharField(max_length=120, blank=True, null=True)
    token_type      = models.CharField(max_length=120, blank=True, null=True)
    expires_at      = models.IntegerField(blank=True, null=True)
    expires_in      = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.app.name