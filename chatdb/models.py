from django.db import models


class DatabaseConfig(models.Model):
    DB_TYPES = [
        ('POSTGRESQL', 'PostgreSQL'),
        ('MYSQL', 'MySQL'),
        # more as necessary
    ]
    type = models.CharField(max_length=20, choices=DB_TYPES)
    name = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    external_info = models.TextField(blank=True)

    def __str__(self):
        return self.name
