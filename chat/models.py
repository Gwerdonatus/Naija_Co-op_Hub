from django.db import models
from django.contrib.auth.models import User
from marketplace.models import Product

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_received_messages')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='chat_messages', null=True, blank=True)
    content = models.TextField(blank=True, null=True)  # Allow blank content if image/audio is sent
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    audio = models.FileField(upload_to='chat_audio/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']  # Messages sorted in chronological order

    def __str__(self):
        preview = self.content[:30] if self.content else "Media message"
        return f"From {self.sender} to {self.receiver}: {preview}"

    def mark_as_read(self):
        """Mark message as read"""
        self.is_read = True
        self.save()
