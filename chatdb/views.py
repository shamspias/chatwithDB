from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from django.conf import settings
from django.core.exceptions import ValidationError

from .permissions import HasValidApiKey, HasValidSuperApiKey
from .models import SystemInfo, ModelInfo, ApiKey, DatabaseConfig
from .serializers import ApiKeySerializer

from .tasks import get_bot_response


class ChatView(APIView):
    """
    API View for Chat
    """
    permission_classes = [HasValidApiKey]
    parser_classes = [JSONParser]

    def post(self, request):
        history = request.data.get('history', None)
        reference_limit = request.data.get('reference_limit', 1)
        conversation_history = request.data.get('history_data', [])
        user_message = request.data.get('message', None)
        language = request.data.get('language', None)
        user_namespace = request.data.get('user_namespace', None)

        # Get system prompt from site settings
        try:
            system_prompt_obj = SystemInfo.objects.first()
            system_prompt = system_prompt_obj.prompt
            if history is None:
                history = system_prompt_obj.history
            if reference_limit == 1:
                reference_limit = system_prompt_obj.reference_limit
        except Exception as e:
            system_prompt = "You are custom_ai_chat AI you can do anything you want."
            if history is None:
                history = 3
            reference_limit = 1
            print("Error:" + str(e))

        # Get the last given conversations

        if len(conversation_history) > 3:
            last_chats = conversation_history[-3:]
        else:
            last_chats = conversation_history

        message_list = []
        for chat in last_chats:
            message_list.append({"role": "user", "content": chat.user_message})
            if chat.bot_message:  # Make sure the bot message exists before adding it.
                message_list.append({"role": "assistant", "content": chat.bot_message})
        message_list.append({"role": "user", "content": user_message})

        try:
            vector_storage_obj = VectorStorage.objects.first()
            provider_name = vector_storage_obj.provider_name
            vector_api_key = vector_storage_obj.api_key
            environment_name = vector_storage_obj.environment_name
            vector_index_name = vector_storage_obj.index_name
            if user_namespace is None:
                name_space = vector_storage_obj.name_space
            else:
                name_space = user_namespace

        except Exception as e:
            provider_name = "Pinecone"
            vector_api_key = settings.PINECONE_API_KEY
            environment_name = settings.PINECONE_ENVIRONMENT
            vector_index_name = settings.PINECONE_INDEX_NAME

            if user_namespace is None:
                name_space = settings.PINECONE_NAMESPACE_NAME
            else:
                name_space = user_namespace
            print(str(e))

        try:
            ai_model_obj = ModelInfo.objects.first()
            model_from = ai_model_obj.model_from
            api_key = ai_model_obj.api_key
            model_name = ai_model_obj.model_name
            model_endpoint = ai_model_obj.model_endpoint
            model_api_version = ai_model_obj.model_api_version
            temperature = ai_model_obj.temperature

            if model_from == "open_ai":
                task = get_bot_response.apply_async(
                    args=[message_list, system_prompt, language, name_space, model_from, model_name, api_key, "",
                          "", vector_api_key, environment_name, vector_index_name, reference_limit, temperature])
                bot_message = task.get()
            else:
                task = get_bot_response.apply_async(
                    args=[message_list, system_prompt, language, name_space, model_from, model_name, api_key,
                          model_endpoint, model_api_version, vector_api_key, environment_name, vector_index_name,
                          reference_limit, temperature])
                bot_message = task.get()

        except Exception as e:
            model_from = "open_ai"
            print("Error: {}".format(str(e)))
            temperature = 1
            # Start the get_bot_response task
            task = get_bot_response.apply_async(
                args=[message_list, system_prompt, language, name_space, model_from, "", "", "", "",
                      vector_api_key, environment_name, vector_index_name, reference_limit, temperature])
            bot_message = task.get()

        return Response({'message': bot_message}, status=status.HTTP_200_OK)


class CreateAPIKeyView(APIView):
    """
    API View to create API key
    """
    permission_classes = [HasValidSuperApiKey]

    def post(self, request):
        username = request.data.get('username', None)
        if username is not None:
            # Checking if username already exists
            if ApiKey.objects.filter(username=username).exists():
                return Response({'detail': 'Username already exists, please use another username.'},
                                status=status.HTTP_400_BAD_REQUEST)

        apikey_serializer = ApiKeySerializer(data=request.data)

        if apikey_serializer.is_valid():
            try:
                apikey = apikey_serializer.save()
                apikey.is_super_api = False
                apikey.save()
                return Response(apikey_serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                # This is raised if a unique constraint on key fails
                if 'key' in e.message_dict:
                    return Response({'detail': 'Key already exists.'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    raise
        else:
            return Response(apikey_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
