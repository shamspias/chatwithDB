from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Document


class DocumentAdmin(admin.ModelAdmin):
    """
    Admin View for Document
    """
    list_display = ('id', 'index_name', 'file', 'is_trained', 'uploaded_at', 'train_button')
    search_fields = ('file', 'index_name')

    def train_button(self, obj):
        train_url = reverse('train_view', args=[obj.pk])
        return format_html('<a class="button" href="{}">{}</a>', train_url, "Train")


admin.site.register(Document, DocumentAdmin)
