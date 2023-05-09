"""For production, we'll automatically generate settings from prod.py via ci/cd script"""
import os
from dotenv import load_dotenv

load_dotenv()
# DEV = False
env_name = os.getenv('ENV_NAME', 'local')

from .key_values import *

if env_name == "prod":
    from .production import *
elif env_name == "dev":
    from .development import *
else:
    from .local import *