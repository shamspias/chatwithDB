from django.contrib import admin
from .models import Chat, CustomPrompt


class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'user_message', 'bot_message', 'timestamp')
    search_fields = ('user_id',)


admin.site.register(Chat, ChatAdmin)
admin.site.register(CustomPrompt)
