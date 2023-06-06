import openai
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from .pinecone_healper import (
    PineconeManager,
    PineconeIndexManager,

)

from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI

openai.api_key = settings.OPENAI_API_KEY

model_name = settings.OPENAI_AI_MODEL

PINECONE_API_KEY = settings.PINECONE_API_KEY
PINECONE_ENVIRONMENT = settings.PINECONE_ENVIRONMENT
PINECONE_INDEX_NAME = settings.PINECONE_INDEX_NAME
OPENAI_API_KEY = settings.OPENAI_API_KEY

logger = get_task_logger(__name__)

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)


def get_pinecone_index(index_name, name_space):
    pinecone_manager = PineconeManager(PINECONE_API_KEY, PINECONE_ENVIRONMENT)
    pinecone_index_manager = PineconeIndexManager(pinecone_manager, index_name)

    try:
        pinecone_index = Pinecone.from_existing_index(index_name=pinecone_index_manager.index_name,
                                                      embedding=embeddings, namespace=settings.PINECONE_NAMESPACE_NAME)
        # pinecone_index = Pinecone.from_existing_index(index_name=pinecone_index_manager.index_name,
        #                                               namespace=name_space, embedding=embeddings)
        return pinecone_index

    except Exception as e:
        logger.error(f"Failed to load Pinecone index: {e}")
        return None


@shared_task
def get_bot_response(message_list, system_prompt, language, name_space):
    # Load the Pinecone index
    base_index = get_pinecone_index(PINECONE_INDEX_NAME, name_space)

    if base_index:
        # Add extra text to the content of the last message
        last_message = message_list[-1]

        # Get the most similar documents to the last message
        try:
            docs = base_index.similarity_search(query=last_message["content"], k=5)

            updated_content = last_message["content"] + "\n\n"
            for doc in docs:
                updated_content += doc.page_content + "\n\n"
        except Exception as e:
            logger.error(f"Failed to get similar documents: {e}")
            updated_content = last_message.content

        # Create a new HumanMessage object with the updated content
        # updated_message = HumanMessage(content=updated_content)
        updated_message = {"role": "user", "content": updated_content}

        # Replace the last message in message_list with the updated message
        message_list[-1] = updated_message

    gpt3_stream_response = openai.ChatCompletion.create(
        model=model_name,
        stream=True,
        messages=[
                     {"role": "system",
                      "content": f"{system_prompt} {language} only."},
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
