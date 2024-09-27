import os

import urllib.parse


DATABASE_HOST = os.environ["DATABASE_HOST"]
DATABASE_NAME = os.environ["DATABASE_NAME"]
DATABASE_USER = os.environ["DATABASE_USER"]
DATABASE_PASSWORD = os.environ["DATABASE_PASSWORD"]
# DATABASE_API_KEY = os.environ["DATABASE_API_KEY"]
DATABASE_URL = f"postgresql://{DATABASE_USER}:{urllib.parse.quote_plus(DATABASE_PASSWORD)}@{DATABASE_HOST}/{DATABASE_NAME}"
