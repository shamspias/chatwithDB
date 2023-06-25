from django.urls import path
from .views import ChatView, CreateAPIKeyView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
    path('create/apikey/', CreateAPIKeyView.as_view(), name='create-apikey'),
]
