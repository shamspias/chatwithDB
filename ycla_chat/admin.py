from django.contrib import admin
from .models import Chat, SystemInfo, ApiKey, ModelInfo, VectorStorage


class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'user_message', 'bot_message', 'timestamp')
    search_fields = ('user_id',)


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('username', 'key',)
    search_fields = ('username', 'key',)


admin.site.register(Chat, ChatAdmin)
admin.site.register(SystemInfo)
admin.site.register(ModelInfo)
admin.site.register(VectorStorage)
