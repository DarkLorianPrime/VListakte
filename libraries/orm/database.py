from os import getenv

from databases import Database
from dotenv import load_dotenv

load_dotenv()
host = getenv("POSTGRES_HOST")
database = getenv("POSTGRES_NAME")
user = getenv("POSTGRES_USER")
password = getenv("POSTGRES_PASSWORD")
db = Database(f'postgres://{host}/{database}', user=user, password=password)