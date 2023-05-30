import openai
from celery import shared_task
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

model_name = settings.OPENAI_AI_MODEL


@shared_task
def get_bot_response(message_list, system_prompt, language):
    gpt3_stream_response = openai.ChatCompletion.create(
        model=model_name,
        stream=True,
        messages=[
                     {"role": "system",
                      "content": f"{system_prompt} you always replay in {language} never replay other then {language} even if your previous conversation in other language still you will replay in {language}"},
                 ] + message_list
    )

    response_text = ""

    # Collect the streamed responses
    for i in gpt3_stream_response:
        if 'choices' in i and i['choices']:
            if 'delta' in i['choices'][0] and 'content' in i['choices'][0]['delta']:
                response_text += i['choices'][0]['delta']['content']

    # bot_message = gpt3_response["choices"][0]["message"]["content"].strip()

    return response_text
