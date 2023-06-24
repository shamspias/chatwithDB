import os
from urllib.parse import quote

# Celery


USE_SQS = bool(os.getenv('USE_SQS', False))

if USE_SQS:
    # AWS
    AWS_ACCESS_KEY = quote(os.getenv('AWS_ACCESS_KEY'), safe='')
    AWS_SECRET_KEY = quote(os.getenv('AWS_SECRET_KEY'), safe='')
    REGION_NAME = quote(os.getenv('REGION_NAME'), safe='')
    QUEUE_NAME = quote(os.getenv('QUEUE_NAME'), safe='')

    """
    AWS celery configuration
    """

    BROKER_URL = 'sqs://{access_key}:{secret_key}@'.format(
        access_key=AWS_ACCESS_KEY,
        secret_key=AWS_SECRET_KEY,
    )
    # RESULT_BACKEND = '{}{}/{}celery'.format(BROKER_URL, REGION_NAME, QUEUE_NAME)

    BROKER_TRANSPORT_OPTIONS = {
        'region': REGION_NAME,
        'visibility_timeout': 60,  # 1 minutes
        # 'polling_interval': 5,  # 5 seconds
        # 'queue_name_prefix': QUEUE_NAME
    }

    # CELERY namespaced
    CELERY_BROKER_URL = BROKER_URL
    CELERY_BROKER_TRANSPORT_OPTIONS = BROKER_TRANSPORT_OPTIONS
    # CELERY_TASK_DEFAULT_QUEUE = QUEUE_NAME

    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'UTC'
    CELERY_RESULT_BACKEND = 'django-db'  # using django-celery-results
    CELERY_CACHE_BACKEND = 'django-cache'

else:
    BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379')
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Open AI key
OPENAI_API_KEY = os.getenv('OPEN_AI_KEY')
OPENAI_AI_API_VERSION = os.getenv('OPENAI_AI_API_VERSION')
OPENAI_AI_MODEL_NAME = os.getenv('OPENAI_AI_MODEL_NAME')

# Pinecone
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
PINECONE_NAMESPACE_NAME = os.getenv('PINECONE_NAMESPACE_NAME')

# Admin Site Config
ADMIN_SITE_HEADER = os.getenv('ADMIN_SITE_HEADER')
ADMIN_SITE_TITLE = os.getenv('ADMIN_SITE_TITLE')
ADMIN_SITE_INDEX = os.getenv('ADMIN_SITE_INDEX')

# API Panel

API_TITLE = os.getenv('API_TITLE', "Title")
API_DESCRIPTION = os.getenv('API_DESCRIPTION', "Documentation")
API_DEFAULT_VERSION = os.getenv('API_DEFAULT_VERSION', "v1")

# OAuth2 settings
APPLICATION_NAME = os.getenv('APPLICATION_NAME', 'chatbot')
