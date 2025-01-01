from bot.helpers.helper_funcs.handlers import CustomCommandHandler, CustomRegexHandler
import logging
from logging.handlers import TimedRotatingFileHandler

import datetime
import sys
# pip install -r requirements.txt

from telegram import __version__ as lver  # noqa: F401
import telegram.ext as tg

from bot.config import *  # noqa: F403
from bot.config import BOT_TOKEN, WORKERS, ALLOW_EXCL

# Configurar el formato del registro
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)

# Obtener la fecha actual como una cadena en el formato 'YYYY-MM-DD'
current_date = datetime.datetime.now().strftime("%Y-%m-%d")

# Configurar el controlador del archivo de registro para que tenga el nombre de la fecha actual
log_filename = f"log_{current_date}.txt"
file_handler = TimedRotatingFileHandler(
    log_filename, when="midnight", backupCount=7, encoding="utf-8"
)
file_handler.setFormatter(logging.Formatter(log_format))

# Agregar el controlador del archivo de registro al sistema de registro
logging.getLogger("").addHandler(file_handler)

# Ejemplo de cómo usar el registro
# logger = logging.getLogger(__name__) #recmendado
LOGGER = logging.getLogger(__name__)
# logger.info('Este mensaje será registrado en el archivo con el nombre de la fecha actual.')

# # enable logging
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     handlers=[logging.FileHandler('log.txt'), logging.StreamHandler()],
#     level=logging.INFO)


# if version < 3.6, stop bot.
python_version = f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}"
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    LOGGER.error(
        "You MUST have a python version of at least 3.6! Multiple features depend on this. Bot quitting."
    )
    quit(1)

if sys.platform.startswith("win"):
    # windows
    # print('windows')
    LOGGER.info("SO > windows")
elif sys.platform.startswith("darwin"):
    # MacOs
    # print('MacOs')
    LOGGER.info("SO > MacOs")
elif sys.platform.startswith("linux"):
    # linux
    # print('linux')
    LOGGER.info("SO > linux")
else:
    print("Sorry, operating system not supported")
    # exit(0)

updater = tg.Updater(
    token=BOT_TOKEN,
    use_context=True,
    workers=WORKERS,  # , base_url=BASE_URL, base_file_url=BASE_FILE_URL
    request_kwargs={'read_timeout': 20, 'connect_timeout': 15}
)

# bot = updater.bot
upd_dis = updater.dispatcher
# job_queue = updater.job_queue
# dispatcher = updater.dispatcher

# Load at end to ensure all prev variables have been set

# make sure the regex handler can take extra kwargs
tg.RegexHandler = CustomRegexHandler


# if not ALLOW_EXCL:
# tg.CommandHandler = CustomCommandHandler
