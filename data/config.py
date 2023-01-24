import logging.config

from os import getenv
from dotenv import load_dotenv
from json import loads
from colorama import Fore, Back, Style

from pathlib import Path, PurePath

assbot_path = Path().absolute()

def get_content(filename: str) -> dict:
    """
    Takes a filename (path) and returns its content in a dictionary
    """
    filename = PurePath(assbot_path, Path(filename))
    with open(filename) as f:
        t = loads(f.read())
    return t

# LOADS DATA FROM JSON

# global varibles
__version__, DB_NAME, USER_RATE_LIMIT, IS_DEBUG, LANGUAGE = get_content('data/cfg/global.json').values()

# long messages
long_messages = get_content(f"data/language_packs/{LANGUAGE}.json")
long_messages["about"] %= __version__

# logging config
LOGGING_CONFIG = get_content('data/cfg/logger.json')

# emojis for /statistic
LUCK_win_emojis, LUCK_fail_emojis, STATISTIC_top_emojis = get_content('data/language_packs/emojis.json').values()


if not IS_DEBUG:
    LOGGING_CONFIG["loggers"]["assbot_logger"]["level"] = "INFO"

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('assbot_logger')
logger.debug("Logger created successfully!")

if IS_DEBUG:
    logger.warning(Back.RED + " DEBUG MODE is ON! " + Style.RESET_ALL)
else:
    logger.info(Back.GREEN + " Debug mode is off " + Style.RESET_ALL)

# Loading local .env file
load_dotenv()
logger.debug("Env variables loaded successfully!")

try:
    TOKEN = getenv("TOKEN")
    OWNER = getenv("OWNER")

    if TOKEN is None:
        raise TypeError
    if OWNER is None:
        logger.info("OWNER's id isn't set")
        SUPER_USERS = []
    else:
        SUPER_USERS = [int(OWNER)]
except TypeError:
    logger.critical(".env file is empty or does\'nt exist!")
    exit(-1)
