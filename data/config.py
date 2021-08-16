from os import getenv
from dotenv import load_dotenv

load_dotenv()  # Initialization

DB_NAME = "list"  # Database name

TOKEN = getenv("TOKEN")  # Get token
SUPER_USERS = [
    
]  # админы
