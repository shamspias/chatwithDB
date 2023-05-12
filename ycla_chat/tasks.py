import openai
from celery import shared_task
from django.conf import settings

from .models import CustomPrompt

# Get system prompt from site settings
try:
    system_prompt_obj = CustomPrompt.objects.first()
    system_prompt = system_prompt_obj.prompt
    language = system_prompt_obj.language
except Exception as e:
    system_prompt = "You are YCLA AI you can do anything you want."
    language = "English"
    print("Error:" + str(e))

openai.api_key = settings.OPENAI_API_KEY


@shared_task
def get_bot_response(message_list):
    gpt3_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                     {"role": "system",
                      "content": f"{system_prompt} you always replay in {language}"},
                 ] + message_list
    )
    bot_message = gpt3_response["choices"][0]["message"]["content"].strip()

    return bot_message
