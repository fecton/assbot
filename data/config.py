import logging.config

from os import getenv
from dotenv import load_dotenv
from data.logger_config import LOGGING_CONFIG
from data.global_variables import *
from colorama import Fore, Back, Style

if not IS_DEBUG:
    LOGGING_CONFIG["loggers"]["assbot_logger"]["level"] = "INFO"

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('assbot_logger')
logger.debug("Logger created successfully!")

if IS_DEBUG:
    logger.warning(Back.RED + " DEBUG MODE is ON! " + Style.RESET_ALL)
else:
    logger.warning(Back.GREEN + " Debug mode is off " + Style.RESET_ALL)

# Loading local .env file
load_dotenv()
logger.debug("Env variables loaded successfully!")

try:
    # TOKEN from BotFather: @BotFather
    TOKEN = getenv("TOKEN")
    # Your id from: @RawDataBot
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
