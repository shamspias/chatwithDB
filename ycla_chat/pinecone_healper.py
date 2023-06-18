import os
import pinecone
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit
import mimetypes
from django.conf import settings
from langchain.document_loaders import (
    CSVLoader,
    UnstructuredWordDocumentLoader,
    PyPDFLoader,
    WebBaseLoader,
    Docx2txtLoader,
)
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone

OPENAI_API_KEY = settings.OPENAI_API_KEY

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)


class PineconeManager:
    """
    This class is used to manage the Pinecone Indexes
    """

    def __init__(self, api_key, environment):
        pinecone.init(
            api_key=api_key,
            environment=environment
        )

    def list_of_indexes(self):
        try:
            pinecone_index_list = pinecone.list_indexes()
            print("List of Pinecone Indexes: ")
            print(pinecone_index_list)
            print("____________________________________________________")
            return pinecone_index_list
        except Exception as e:
            print("Error in listing the Pinecone Indexes: ", e)
            print("____________________________________________________")
            raise Exception("Error in listing the Pinecone Indexes: ", e)

    def create_index(self, index_name, dimension, metric):
        pinecone.create_index(name=index_name, dimension=dimension, metric=metric)

    def delete_index(self, index_name):
        pinecone.delete_index(index_name)


class PineconeIndexManager:
    """
    This class is used to manage the Pinecone Indexes
    """

    def __init__(self, pinecone_manager, index_name):
        self.pinecone_manager = pinecone_manager
        self.index_name = index_name

    def index_exists(self):
        active_indexes = self.pinecone_manager.list_of_indexes()
        return self.index_name in active_indexes

    def create_index(self, dimension, metric):
        self.pinecone_manager.create_index(self.index_name, dimension, metric)

    def delete_index(self):
        self.pinecone_manager.delete_index(self.index_name)


class URLHandler:
    @staticmethod
    def is_valid_url(url):
        parsed_url = urlsplit(url)
        return bool(parsed_url.scheme) and bool(parsed_url.netloc)

    @staticmethod
    def extract_links(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                absolute_url = urljoin(url, href)
                if URLHandler.is_valid_url(absolute_url):
                    links.append(absolute_url)

        return links

    @staticmethod
    def extract_links_from_websites(websites):
        all_links = []

        for website in websites:
            links = URLHandler.extract_links(website)
            all_links.extend(links)

        return all_links


class DocumentLoaderFactory:
    @staticmethod
    def get_loader(file_path_or_url):
        if file_path_or_url.startswith("http://") or file_path_or_url.startswith("https://"):
            handle_website = URLHandler()
            return WebBaseLoader(handle_website.extract_links_from_websites([file_path_or_url]))
        else:
            mime_type, _ = mimetypes.guess_type(file_path_or_url)

            if mime_type == 'application/pdf':
                return PyPDFLoader(file_path_or_url)
            elif mime_type == 'text/csv':
                return CSVLoader(file_path_or_url)
            elif mime_type in ['application/msword',
                               'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                return Docx2txtLoader(file_path_or_url)
                # return UnstructuredWordDocumentLoader(file_path_or_url)
            else:
                raise ValueError(f"Unsupported file type: {mime_type}")


def build_or_update_pinecone_index(file_path, index_name, name_space, pinecone_api_key, pinecone_environment):
    """
    This function is used to build or update the Pinecone Index
    """
    pinecone_index_manager = PineconeIndexManager(PineconeManager(pinecone_api_key, pinecone_environment), index_name)
    loader = DocumentLoaderFactory.get_loader(file_path)
    pages = loader.load_and_split()

    if pinecone_index_manager.index_exists():
        print("Updating the model")
        pinecone_index = Pinecone.from_documents(pages, embeddings, index_name=pinecone_index_manager.index_name,
                                                 namespace=name_space)

    else:
        print("Training the model")
        pinecone_index_manager.create_index(dimension=1536, metric="cosine")
        pinecone_index = Pinecone.from_documents(documents=pages, embedding=embeddings,
                                                 index_name=pinecone_index_manager.index_name,
                                                 namespace=name_space)
    return pinecone_index
