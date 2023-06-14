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

logger = get_task_logger(__name__)


def get_pinecone_index(index_name, name_space, embeddings, vector_api_key, environment_name):
    pinecone_manager = PineconeManager(vector_api_key, environment_name)
    pinecone_index_manager = PineconeIndexManager(pinecone_manager, index_name)

    try:
        pinecone_index = Pinecone.from_existing_index(index_name=pinecone_index_manager.index_name,
                                                      embedding=embeddings, namespace=name_space)
        # pinecone_index = Pinecone.from_existing_index(index_name=pinecone_index_manager.index_name,
        #                                               namespace=name_space, embedding=embeddings)
        return pinecone_index

    except Exception as e:
        logger.error(f"Failed to load Pinecone index: {e}")
        return None


@shared_task
def get_bot_response(message_list, system_prompt, language, name_space, model_from, model_name, api_key, model_endpoint,
                     model_api_version, vector_api_key, environment_name, vector_index_name):
    # if model_from == "azure":
    #     embeddings = OpenAIEmbeddings(openai_api_type=model_from, openai_api_base=model_endpoint,
    #                                   openai_api_key=api_key, openai_api_version=model_api_version, deployment="")
    # else:
    #     embeddings = OpenAIEmbeddings(openai_api_type="open_ai", openai_api_base="https://api.openai.com/v1",
    #                                   openai_api_key=OPENAI_API_KEY,
    #                                   openai_api_version=None, )

    embeddings = OpenAIEmbeddings(openai_api_type="open_ai", openai_api_base="https://api.openai.com/v1",
                                  openai_api_key=api_key,
                                  openai_api_version=None, )
    # Load the Pinecone index
    base_index = get_pinecone_index(vector_index_name, name_space, embeddings, vector_api_key, environment_name)

    if base_index:
        # Add extra text to the content of the last message
        last_message = message_list[-1]

        query_text = last_message["content"]

        # Get the most similar documents to the last message
        try:
            docs = base_index.similarity_search(query=query_text, k=2)

            updated_content = query_text + "\n\nreference:\n"
            for doc in docs:
                updated_content += doc.page_content + "\n\n"
        except Exception as e:
            logger.error(f"Failed to get similar documents: {e}")
            updated_content = query_text

        # Create a new HumanMessage object with the updated content
        # updated_message = HumanMessage(content=updated_content)
        updated_message = {"role": "user", "content": updated_content}

        # Replace the last message in message_list with the updated message
        message_list[-1] = updated_message

    if model_from == "azure":
        openai.api_type = model_from
        openai.api_base = model_endpoint
        openai.api_version = model_api_version
        openai.api_key = api_key

        gpt3_stream_response = openai.ChatCompletion.create(
            engine=model_name,
            stream=True,
            messages=[
                         {"role": "system",
                          "content": f"{system_prompt} {language} only."},
                     ] + message_list
        )
    else:
        openai.api_key = settings.OPENAI_API_KEY
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
