from django import forms
from django.contrib.auth.models import User
from .models import Profile, Skill

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileForm(forms.ModelForm):
    # Use a multiple choice field for skills with checkboxes for a user-friendly selection.
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select the skills you possess"
    )
    
    class Meta:
        model = Profile
        fields = [
            'phone_number',
            'address',
            'profile_picture',
            'role',
            'bio',
            'custom_url',
            'skills',
            'cooperative_name',
            'membership_role',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell us about yourself'}),
            'custom_url': forms.TextInput(attrs={'placeholder': 'Your custom URL'}),
            'address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Your address'}),
        }
