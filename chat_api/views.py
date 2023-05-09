from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django.core.exceptions import ObjectDoesNotExist

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .tasks import get_chat_reply, generate_conversation_title


class LastMessagesPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 10


class ConversationListCreate(generics.ListCreateAPIView):
    """
    List all conversations or create a new conversation.
    """
    serializer_class = ConversationSerializer

    def get_queryset(self):
        username = self.request.query_params.get('username')
        return Conversation.objects.filter(username=username).order_by('created_at')

    def perform_create(self, serializer):
        username = self.request.data.get('username')
        serializer.save(username=username)


class ConversationDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a conversation.
    """
    serializer_class = ConversationSerializer

    def get_queryset(self):
        username = self.request.query_params.get('username')
        return Conversation.objects.filter(username=username)

    def delete(self, request, *args, **kwargs):
        conversation = self.get_object()
        username = request.data.get('username')
        if conversation.username != username:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)


class ConversationArchive(APIView):
    """
    Add or remove a conversation from archive
    """

    def patch(self, request, pk):
        username = request.data.get('username')
        conversation = get_object_or_404(Conversation, id=pk, username=username)
        if conversation.archive:
            conversation.archive = False
            conversation.save()
            return Response({"message": "remove from archive"}, status=status.HTTP_200_OK)
        else:
            conversation.archive = True
            conversation.save()
            return Response({"message": "add to archive"}, status=status.HTTP_200_OK)


class ConversationFavourite(APIView):
    """
    Add or remove a conversation from favourites
    """

    def patch(self, request, pk):
        username = request.data.get('username')
        conversation = get_object_or_404(Conversation, id=pk, username=username)
        if conversation.favourite:
            conversation.favourite = False
            conversation.save()
            return Response({"message": "remove from favourite"}, status=status.HTTP_200_OK)
        else:
            conversation.favourite = True
            conversation.save()
            return Response({"message": "add to favourite"}, status=status.HTTP_200_OK)


class ConversationDelete(APIView):
    """
    Delete a conversation
    """

    def delete(self, request, pk):
        username = request.data.get('username')
        conversation = get_object_or_404(Conversation, id=pk, username=username)
        conversation.delete()
        return Response({"message": "conversation deleted"}, status=status.HTTP_200_OK)


class MessageList(generics.ListAPIView):
    """
    List all messages in a conversation
    """
    serializer_class = MessageSerializer
    pagination_class = LastMessagesPagination

    def get_queryset(self):
        username = self.request.query_params.get('username')
        conversation = get_object_or_404(Conversation, id=self.kwargs['conversation_id'], username=username)
        return Message.objects.filter(conversation=conversation).select_related('conversation')


class MessageCreate(generics.CreateAPIView):
    """
    Create a new message in a conversation
    """
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        username = self.request.data.get('username')
        conversation = get_object_or_404(Conversation, id=self.kwargs['conversation_id'], username=username)
        serializer.save(conversation=conversation, is_from_user=True)

        messages = Message.objects.filter(conversation=conversation).order_by('-created_at')[:10][::-1]

        message_list = []
        for msg in messages:
            if msg.is_from_user:
                message_list.append({"role": "user", "content": msg.content})
            else:
                message_list.append({"role": "assistant", "content": msg.content})

        task = get_chat_reply.apply_async(args=(message_list, username))
        print(message_list)
        response = task.get()
        return [response, conversation.id, messages[0].id]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_list = self.perform_create(serializer)
        assistant_response = response_list[0]
        conversation_id = response_list[1]
        last_user_message_id = response_list[2]

        try:
            message = Message(
                conversation_id=conversation_id,
                content=assistant_response,
                is_from_user=False,
                in_reply_to_id=last_user_message_id
            )
            message.save()

        except ObjectDoesNotExist:
            error = f"Conversation with id {conversation_id} does not exist"
            Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_mgs = str(e)
            error = f"Failed to save GPT-3 response as a message: {error_mgs}"
            Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response({"response": assistant_response}, status=status.HTTP_200_OK, headers=headers)


class ConversationRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    Retrieve View to update or get the title
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    lookup_url_kwarg = 'conversation_id'

    def retrieve(self, request, *args, **kwargs):
        conversation = self.get_object()

        if conversation.title == "Empty":
            messages = Message.objects.filter(conversation=conversation)

            if messages.exists():
                message_list = []
                for msg in messages:
                    if msg.is_from_user:
                        message_list.append({"role": "user", "content": msg.content})
                    else:
                        message_list.append({"role": "assistant", "content": msg.content})

                task = generate_conversation_title.apply_async(args=(message_list,))
                my_title = task.get()
                # if length of title is greater than 55, truncate it
                my_title = my_title[:30]
                conversation.title = my_title
                conversation.save()
                serializer = self.get_serializer(conversation)
                return Response(serializer.data)
            else:
                return Response({"message": "No messages in conversation."}, status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = self.get_serializer(conversation)
            return Response(serializer.data)
