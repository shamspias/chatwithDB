import requests
import tempfile
import os

from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.views import View
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import Document
from ycla_chat.models import VectorStorage
from ycla_chat.pinecone_healper import build_or_update_pinecone_index

User = get_user_model()


class TrainView(View):
    """
    View to train a Pinecone index
    """

    def get(self, request, object_id):
        # Check if user is staff or superuser
        if not request.user.is_staff and not request.user.is_superuser:
            return HttpResponseForbidden("You don't have permission to access this page.")

        document = Document.objects.get(pk=object_id)
        index_name = document.index_name
        namespace = User.objects.get(pk=request.user.id).username

        # Download the file and save it to a temporary directory
        file_url = document.file.url
        response = requests.get(file_url)
        temp_dir = tempfile.mkdtemp()
        file_name = os.path.join(temp_dir, os.path.basename(file_url))

        with open(file_name, 'wb') as f:
            f.write(response.content)

        file_path = file_name

        try:
            vector_index_obj = VectorStorage.objects.first()
            pinecone_api_key = vector_index_obj.pinecone_api_key
            pinecone_environment = vector_index_obj.pinecone_environment
        except Exception as e:
            pinecone_api_key = settings.PINECONE_API_KEY
            pinecone_environment = settings.PINECONE_ENVIRONMENT
            print(str(e))

        # Load and process files
        build_or_update_pinecone_index(file_path, index_name, namespace, pinecone_api_key, pinecone_environment)

        # Update is_trained to True
        document.is_trained = True
        document.save()

        # Clean up the temporary directory
        os.remove(file_path)
        os.rmdir(temp_dir)

        # Redirect to Django admin with a success message
        messages.success(request, "Training complete.")
        admin_url = reverse('admin:datatrain_document_change', args=[object_id])
        return HttpResponseRedirect(admin_url)
