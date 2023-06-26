import uuid
from django.db import models


class DatabaseConfig(models.Model):
    DB_TYPES = [
        ('POSTGRESQL', 'PostgreSQL'),
        ('MYSQL', 'MySQL'),
        ('MONGODB', 'MongoDB'),
        # more as necessary
    ]
    type = models.CharField(max_length=20, choices=DB_TYPES)
    name = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    external_info = models.TextField(blank=True)

    class Meta:
        verbose_name = "Database Configuration"
        verbose_name_plural = "Database Configurations"

    def __str__(self):
        return self.name


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


class SystemInfo(models.Model):
    prompt = models.TextField(null=True, blank=True)
    history = models.IntegerField(default=3)
    reference_limit = models.PositiveIntegerField(default=2)

    class Meta:
        verbose_name_plural = "System Info"

    def __str__(self):
        if self.prompt:
            return self.prompt[:50]
        else:
            return "Custom Prompt"


class ModelInfo(models.Model):
    model_from = models.CharField(max_length=100, null=True, blank=True)
    api_key = models.TextField(null=True, blank=True)
    model_name = models.CharField(max_length=255, null=True, blank=True)
    temperature = models.FloatField(default=1.0)
    model_endpoint = models.CharField(max_length=255, null=True, blank=True)
    model_api_version = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        if self.model_from:
            return self.model_name[:50]
        else:
            return "Custom Model"
