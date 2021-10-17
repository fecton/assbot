from os import getenv
from dotenv import load_dotenv

load_dotenv()  # Initialization

DB_NAME = "list.sqlite3"  # Database name

TOKEN = getenv("TOKEN")  # Get token
SUPER_USERS = [int(getenv("OWNER"))]  # админы
