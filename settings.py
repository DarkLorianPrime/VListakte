# Create a database instance, and connect to it.
import os
import dotenv
dotenv.load_dotenv()
SHAtoken = "Px13n4FCGyGoEKrmiYK69c76Ry9wTJkIQh1pjDd0NdJCfQQaEoxObDLjm1qZ3xdxKlCnGx"
database = {
    "host": os.getenv("host"),
    "db": os.getenv("db"),
    "user": os.getenv("user"),
    "password": os.getenv("password")
}
