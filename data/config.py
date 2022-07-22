from os import getenv
from dotenv import load_dotenv

USER_RATE_LIMIT = 60

# Loading local .env file
load_dotenv()  

DB_NAME = "list.sqlite3"  # Database name

try:
    # TOKEN from BotFather: @BotFather
    TOKEN = getenv("TOKEN") 

    if TOKEN is None: raise TypeError

    # Your beautiful telegram id which you can get here: @RawDataBot
    SUPER_USERS = [int(getenv("OWNER"))]
except TypeError:
    print('[ERROR] .env file is empty or does\'nt exist!')
    exit(-1)
