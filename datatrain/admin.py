import os
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Document, Websites


class DocumentAdmin(admin.ModelAdmin):
    """
    Admin View for Document
    """
    list_display = ('file_name', 'index_name', 'is_trained', 'uploaded_at', 'train_button')
    search_fields = ('file', 'index_name')

    def file_name(self, obj):
        return os.path.basename(obj.file.name)

    file_name.short_description = 'File Name'  # Sets the column header

    def train_button(self, obj):
        train_url = reverse('train_view', args=[obj.pk])
        return format_html('<a class="button" href="{}">{}</a>', train_url, "Train")


class WebsiteAdmin(admin.ModelAdmin):
    """
    Admin View for Websites
    """
    list_display = ('address', 'index_name', 'is_trained', 'uploaded_at')
    search_fields = ('address', 'index_name')


admin.site.register(Document, DocumentAdmin)
admin.site.register(Websites, WebsiteAdmin)
