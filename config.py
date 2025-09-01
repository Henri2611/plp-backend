import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": "localhost",
    "user": "root",          # change to your MySQL user
    "password": "Pass@1234",  # change to your MySQL password
    "database": "recipe_db"
}

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
