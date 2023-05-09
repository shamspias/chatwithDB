from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    """
    Tabular Inline View for Message
    """
    model = Message
    extra = 0
    readonly_fields = ('content', 'created_at', 'is_from_user', 'in_reply_to')
    show_change_link = True
    can_delete = False
    ordering = ('created_at',)


class ConversationAdmin(admin.ModelAdmin):
    """
    Admin View for Conversation
    """
    list_display = ('id', 'title', 'username', 'created_at', 'updated_at', 'favourite', 'archive')
    search_fields = ('title', 'username')
    list_filter = ('created_at', 'updated_at', 'favourite', 'archive')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [MessageInline]
    ordering = ('-created_at',)


class MessageAdmin(admin.ModelAdmin):
    """
    Admin View for Message
    """
    list_display = ('id', 'conversation', 'content', 'created_at', 'is_from_user')
    search_fields = ('content',)
    list_filter = ('created_at', 'is_from_user')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)


admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)
