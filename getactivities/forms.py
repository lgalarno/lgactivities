from django import forms

from .models import FetchActivitiesTask


class GetActivitiesTaskForm(forms.ModelForm):
    class Meta:
        model = FetchActivitiesTask
        fields = (
            'start_date',
            'frequency',
            'active'
        )

        widgets = {
            'start_date': forms.DateInput(
                attrs={'type': 'date'}
            )
        }
