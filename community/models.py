from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse

class Community(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, related_name='created_communities', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    members = models.ManyToManyField(User, related_name='communities', blank=True)

    def save(self, *args, **kwargs):
        # Automatically generate a slug from the community name if not provided.
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, related_name='posts', on_delete=models.CASCADE)  # Added Community Link
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    upvotes = models.ManyToManyField(User, related_name='post_upvotes', blank=True)
    downvotes = models.ManyToManyField(User, related_name='post_downvotes', blank=True)

    def total_upvotes(self):
        return self.upvotes.count()

    def total_downvotes(self):
        return self.downvotes.count()

    def __str__(self):
        return f"{self.author.username} - {self.content[:20]}"

    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.author.username})  # Profile link for users


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Renamed from `user` to `author`
    content = models.TextField()
    image = models.ImageField(upload_to='comment_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.id}"

    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.author.username})  # Profile link for users
