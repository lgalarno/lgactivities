from django.contrib import admin

from .models import StravaApp, Token

# Register your models here.
admin.site.register(StravaApp)
admin.site.register(Token)
