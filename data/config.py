from os import getenv
from dotenv import load_dotenv
from .long_messages import long_messages

load_dotenv()  # Initialization

DB_NAME = "list"  # Database name

TOKEN = getenv("TOKEN")  # Get token
SUPER_USERS = [
    817810926,
]  # админы
