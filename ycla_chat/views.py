from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Chat, CustomPrompt
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
            last_chats = Chat.objects.filter(user_id=user_id).order_by('-timestamp')[:10]

            message_list = []
            for chat in last_chats:
                message_list.append({"role": "user", "content": chat.user_message})
                if chat.bot_message:  # Make sure the bot message exists before adding it.
                    message_list.append({"role": "assistant", "content": chat.bot_message})
            message_list = message_list[::-1]  # Reverse the order to maintain the chronological order
            print(message_list)

            # Get system prompt from site settings
            try:
                system_prompt_obj = CustomPrompt.objects.first()
                system_prompt = system_prompt_obj.prompt
            except Exception as e:
                system_prompt = "You are YCLA AI you can do anything you want."
                print("Error:" + str(e))

            # Start the get_bot_response task
            task = get_bot_response.apply_async(args=[message_list, system_prompt, language])
            bot_message = task.get()

            chat = Chat(user_id=user_id, user_message=user_message, bot_message=bot_message)
            chat.save()

            return Response({'message': bot_message}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
