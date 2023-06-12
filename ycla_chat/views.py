from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.conf import settings

from .permissions import HasValidApiKey
from .models import Chat, SystemInfo, ModelInfo, VectorStorage
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

            # Get system prompt from site settings
            try:
                system_prompt_obj = SystemInfo.objects.first()
                system_prompt = system_prompt_obj.prompt
                history = system_prompt_obj.history
            except Exception as e:
                system_prompt = "You are YCLA AI you can do anything you want."
                history = 3
                print("Error:" + str(e))

            # Get the last given conversations
            last_chats = Chat.objects.filter(user_id=user_id).order_by('-timestamp')[:history]

            message_list = []
            for chat in last_chats:
                message_list.append({"role": "user", "content": chat.user_message})
                if chat.bot_message:  # Make sure the bot message exists before adding it.
                    message_list.append({"role": "assistant", "content": chat.bot_message})
            message_list.append({"role": "user", "content": user_message})

            print(message_list)

            try:
                vector_storage_obj = VectorStorage.objects.first()
                provider_name = vector_storage_obj.provider_name
                vector_api_key = vector_storage_obj.api_key
                environment_name = vector_storage_obj.environment_name
                vector_index_name = vector_storage_obj.index_name
                name_space = vector_storage_obj.name_space

            except Exception as e:
                provider_name = "Pinecone"
                vector_api_key = settings.PINECONE_API_KEY
                environment_name = settings.PINECONE_ENVIRONMENT
                vector_index_name = settings.PINECONE_INDEX_NAME
                name_space = settings.PINECONE_NAMESPACE_NAME
                print(str(e))

            try:
                ai_model_obj = ModelInfo.objects.first()
                model_from = ai_model_obj.model_from
                api_key = ai_model_obj.api_key
                model_name = ai_model_obj.model_name
                model_endpoint = ai_model_obj.model_endpoint
                model_api_version = ai_model_obj.model_api_version

                if model_from == "openai":
                    task = get_bot_response.apply_async(
                        args=[message_list, system_prompt, language, name_space, model_from, "", "", "", "",
                              vector_api_key, environment_name, vector_index_name])
                    bot_message = task.get()
                else:
                    task = get_bot_response.apply_async(
                        args=[message_list, system_prompt, language, name_space, model_from, model_name, api_key,
                              model_endpoint, model_api_version, vector_api_key, environment_name, vector_index_name])
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
