import os
import uuid
from django.db import models


def upload_to_pinecone(filename):
    basename, ext = os.path.splitext(filename)
    new_filename = f"{basename}_{uuid.uuid4().hex}{ext}"
    return f'documents/pinecone/{new_filename}'


class Document(models.Model):
    file = models.FileField(upload_to=upload_to_pinecone)
    index_name = models.CharField(max_length=255)
    is_trained = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
