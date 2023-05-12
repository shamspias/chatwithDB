from celery import shared_task
from django.conf import settings
import openai
import logging

from ycla_chat.models import CustomPrompt

logger = logging.getLogger(__name__)

# Get system prompt from site settings
try:
    system_prompt_obj = CustomPrompt.objects.first()
    system_prompt = system_prompt_obj.prompt
    language = system_prompt_obj.language
except Exception as e:
    system_prompt = "You are YCLA AI you can do anything you want."
    language = "English"
    print("Error:" + str(e))


@shared_task
def get_chat_reply(message_list):
    try:
        openai.api_key = settings.OPENAI_API_KEY
        # Send request to GPT-3 (replace with actual GPT-3 API call)
        gpt3_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                         {"role": "system",
                          "content": "{system_prompt} always speak in {language}"},
                     ] + message_list
        )

        assistant_response = gpt3_response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        logger.error(f"Failed to send request to GPT-3.5: {e}")
        return "Sorry, I'm having trouble understanding you."

    return assistant_response


@shared_task
def generate_conversation_title(message_list):
    try:
        openai.api_key = settings.OPENAI_API_KEY
        # Send request to GPT-3 (replace with actual GPT-3 API call)
        gpt3_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                         {"role": "system",
                          "content": "Summarize and make a very short meaningful title under 24 characters"},
                     ] + message_list
        )
        response = gpt3_response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        logger.error(f"Failed to send request to GPT-3.5: {e}")
        return "Problematic title with error."

    return response
