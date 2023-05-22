import uuid
from django.db import models


class ApiKey(models.Model):
    username = models.CharField(max_length=255)
    key = models.CharField(max_length=255, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.key:
            # Generate a UUID if this is a new instance.
            self.key = str(uuid.uuid4())
        return super().save(*args, **kwargs)


class Chat(models.Model):
    user_id = models.CharField(max_length=255)
    user_message = models.TextField()
    bot_message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id}: {self.user_message}"

    class Meta:
        ordering = ['timestamp']


class CustomPrompt(models.Model):
    prompt = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Custom Prompts"

    def __str__(self):
        if self.prompt:
            return self.prompt[:50]
        else:
            return "Custom Prompt"
