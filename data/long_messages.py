# -*- coding: utf-8 -*-
import json
from aiogram.utils.markdown import escape_md
from data.global_variables import __version__, LANGUAGE

with open(f"data/language_packs/{LANGUAGE}.json") as jsonfile:
    long_messages = json.loads(jsonfile.read())

long_messages["about"] = long_messages["about"] % __version__

