from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)