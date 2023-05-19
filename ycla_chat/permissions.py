from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed
from .models import ApiKey


class HasValidApiKey(permissions.BasePermission):
    message = 'No API Key provided or Invalid API Key.'

    def has_permission(self, request, view):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return False
        try:
            ApiKey.objects.get(key=api_key)
            return True
        except ApiKey.DoesNotExist:
            return False
