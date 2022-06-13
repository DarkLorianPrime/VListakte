# Create a database instance, and connect to it.
import os
import dotenv
dotenv.load_dotenv('.env')
SHAtoken = os.getenv("SHATOKEN")
database = {
    "host": os.getenv("HOST"),
    "db": os.getenv("DB"),
    "user": os.getenv("USER"),
    "password": os.getenv("PASSWORD")
}
