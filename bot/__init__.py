import logging
import os
import sys

import telegram.ext as tg
from bot.config import *

if os.path.exists('log.txt'):
    with open('log.txt', 'r+') as f:
        f.truncate(0)

# enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler('log.txt'), logging.StreamHandler()],
    level=logging.INFO)


LOGGER = logging.getLogger(__name__)

# if version < 3.6, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    LOGGER.error("You MUST have a python version of at least 3.6! Multiple features depend on this. Bot quitting.")
    quit(1)

if sys.platform.startswith("win"):
    # windows
    print('windows')
elif sys.platform.startswith("darwin"):
    # MacOs
    print('MacOs')
elif sys.platform.startswith("linux"):
    # linux
    print('linux')
else:
    print("Sorry, operating system not supported")
    # exit(0)

TOKEN = BOT_TOKEN
updater = tg.Updater(TOKEN, use_context=True, workers=WORKERS)

bot = updater.bot
dispatcher = updater.dispatcher

# Load at end to ensure all prev variables have been set
from bot.modules.helper_funcs.handlers import CustomCommandHandler, CustomRegexHandler

# make sure the regex handler can take extra kwargs
tg.RegexHandler = CustomRegexHandler


if ALLOW_EXCL:
    tg.CommandHandler = CustomCommandHandler