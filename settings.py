# Create a database instance, and connect to it.
import os
import dotenv
dotenv.load_dotenv()
database = {
    "host": os.getenv("host"),
    "db": os.getenv("db"),
    "user": os.getenv("user"),
    "password": os.getenv("password")
}
