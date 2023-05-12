from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Chat
from .serializers import ChatSerializer
from .tasks import get_bot_response


class ChatView(APIView):
    """
    API View for Chat
    """

    def post(self, request):
        serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            user_message = serializer.validated_data['user_message']
            language = request.data.get('language', "English")

            # Get the last 10 conversations
            last_chats = Chat.objects.filter(user_id=user_id).order_by('-timestamp')[:10][::-1]
            message_list = []
            for chat in last_chats:
                message_list.append({"role": "user", "content": chat.user_message})
                message_list.append({"role": "assistant", "content": chat.bot_message})

            # Start the get_bot_response task
            task = get_bot_response.apply_async(args=[message_list, language])
            bot_message = task.get()

            chat = Chat(user_id=user_id, user_message=user_message, bot_message=bot_message)
            chat.save()

            return Response({'message': bot_message}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, user_id):
        chats = Chat.objects.filter(user_id=user_id).order_by('-timestamp')
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)
