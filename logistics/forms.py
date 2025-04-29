# logistics/forms.py
from django import forms
from .models import LogisticCompany

class LogisticCompanyForm(forms.ModelForm):
    class Meta:
        model = LogisticCompany
        fields = ['name', 'email', 'phone', 'address', 'services_offered']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'services_offered': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
