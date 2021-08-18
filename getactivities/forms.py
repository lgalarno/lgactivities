from django import forms

from .models import GetActivitiesTask


class GetActivitiesTaskForm(forms.ModelForm):
    class Meta:
        model = GetActivitiesTask
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
