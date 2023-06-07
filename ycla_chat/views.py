from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .permissions import HasValidApiKey
from .models import Chat, CustomPrompt, ModelInfo
from .serializers import ChatSerializer
from .tasks import get_bot_response


class ChatView(APIView):
    """
    API View for Chat
    """
    permission_classes = [HasValidApiKey]

    def post(self, request):
        serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            user_message = serializer.validated_data['user_message']
            language = request.data.get('language', "English")

            # Get the last 5 conversations
            last_chats = Chat.objects.filter(user_id=user_id).order_by('-timestamp')[:5]

            message_list = []
            for chat in last_chats:
                message_list.append({"role": "user", "content": chat.user_message})
                if chat.bot_message:  # Make sure the bot message exists before adding it.
                    message_list.append({"role": "assistant", "content": chat.bot_message})
            message_list.append({"role": "user", "content": user_message})

            print(message_list)

            # Get system prompt from site settings
            try:
                system_prompt_obj = CustomPrompt.objects.first()
                system_prompt = system_prompt_obj.prompt
                name_space = system_prompt_obj.name_space
            except Exception as e:
                system_prompt = "You are YCLA AI you can do anything you want."
                name_space = "ycla"
                print("Error:" + str(e))

            try:
                ai_model_obj = ModelInfo.objects.first()
                model_from = ai_model_obj.model_from
                api_key = ai_model_obj.api_key
                model_name = ai_model_obj.model_name
                model_endpoint = ai_model_obj.model_endpoint
                model_api_version = ai_model_obj.model_api_version

                if model_from == "openai":
                    task = get_bot_response.apply_async(
                        args=[message_list, system_prompt, language, name_space, model_from])
                    bot_message = task.get()
                else:
                    task = get_bot_response.apply_async(
                        args=[message_list, system_prompt, language, name_space, model_from, model_name, api_key,
                              model_endpoint, model_api_version])
                    bot_message = task.get()

            except Exception as e:
                print(str(e))
                model_from = "openai"
                # Start the get_bot_response task
                task = get_bot_response.apply_async(
                    args=[message_list, system_prompt, language, name_space, model_from])
                bot_message = task.get()

            chat = Chat(user_id=user_id, user_message=user_message, bot_message=bot_message)
            chat.save()

            return Response({'message': bot_message}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
