from rest_framework import permissions
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


class HasValidSuperApiKey(permissions.BasePermission):
    message = 'No API Super Key provided or Invalid Super API Key.'

    def has_permission(self, request, view):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return False
        try:
            super_key = ApiKey.objects.get(key=api_key)
            if super_key.is_super_api:
                return True
            else:
                return False
        except ApiKey.DoesNotExist:
            return False
