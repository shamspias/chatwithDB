from django.db import models


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
    language = models.CharField(default="English", max_length=50)

    class Meta:
        verbose_name_plural = "Custom Prompts"

    def __str__(self):
        return self.language
