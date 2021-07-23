from django import forms
from django.contrib.auth.models import User

from .models import StravaProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )
        widgets = {
            'email': forms.TextInput(attrs={'required': 'true'}),
        }

class StravaProfileForm(forms.ModelForm):
    class Meta:
        model = StravaProfile
        fields = (
            'city',
            'country',
            # 'avatar_url',
        )
