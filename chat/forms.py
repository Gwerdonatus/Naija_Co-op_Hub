
from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["content", "image", "audio"]
        widgets = {
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 1, "placeholder": "Type a message..."}),
        }
