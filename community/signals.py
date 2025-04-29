# community/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment
from notifications.models import Notification
from django.urls import reverse

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        commenter = instance.author  # 🔁 This is the correct field

        # Avoid notifying the commenter if they commented on their own post.
        if post.author != commenter:
            message = f"You have a new comment by {instance.author.username} on your post: \"{post.content[:30]}...\""
            link = reverse('community:community_detail', kwargs={'slug': post.community.slug})

            Notification.objects.create(
                recipient=post.author,
                message=message,
                link=link
            )


