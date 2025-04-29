from django import forms
from django.core.exceptions import ValidationError
from .models import SavingsPool

class SavingsPoolForm(forms.ModelForm):
    class Meta:
        model = SavingsPool
        fields = ['name', 'contribution_amount', 'contribution_frequency', 'start_date', 'end_date']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and start_date >= end_date:
            raise ValidationError("Start date must be before end date. Please correct the dates.")
        return cleaned_data
