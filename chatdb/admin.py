from django.contrib import admin
from .models import DatabaseConfig, Chat, SystemInfo, ApiKey, ModelInfo


class DatabaseConfigAdmin(admin.ModelAdmin):
    """
    Model Admin for database
    """
    list_display = ('name', 'type', 'username', 'host', 'port')  # Fields to display in list view
    search_fields = ('name', 'username',)  # Fields to search
    list_filter = ('type',)  # Fields to filter

    # Hide password in list view
    def get_list_display(self, request):
        self.exclude = ('password',)
        return super(DatabaseConfigAdmin, self).get_list_display(request)

    # Hide password in detail view
    # def get_exclude(self, request, obj=None):
    #     self.exclude = ('password',)
    #     return super(DatabaseConfigAdmin, self).get_exclude(request, obj)


class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'user_message', 'bot_message', 'timestamp')
    search_fields = ('user_id',)


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('username', 'key',)
    search_fields = ('username', 'key',)


admin.site.register(DatabaseConfig, DatabaseConfigAdmin)
admin.site.register(Chat, ChatAdmin)
admin.site.register(SystemInfo)
admin.site.register(ModelInfo)
