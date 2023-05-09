from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chat_api.models import Conversation, Message


class ChatAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        self.conversation = Conversation.objects.create(
            title="Test Conversation",
            username=self.user.username
        )
        self.message = Message.objects.create(
            conversation=self.conversation,
            content="Test message",
            is_from_user=True
        )

    def test_create_conversation(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('chat_api:conversation-list-create')
        response = self.client.post(url, {"title": "New conversation", "username": "testuser"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 2)
        self.assertEqual(Conversation.objects.get(id=2).title, 'New conversation')

    def test_list_conversations(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('chat_api:conversation-list-create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_messages(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('chat_api:message-list', kwargs={'conversation_id': self.conversation.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_message(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('chat_api:message-create', kwargs={'conversation_id': self.conversation.id})
        response = self.client.post(url, {"content": "Another test message", "username": "testuser"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(Message.objects.get(id=2).content, 'Another test message')

# Add more test cases for other views as needed
