import logging
from logging.handlers import TimedRotatingFileHandler
# from bot.helpers.helper_funcs.handlers import CustomCommandHandler, CustomRegexHandler
from bot.config import Config

import datetime
import sys
# pip install -r requirements.txt

config = Config()

if not config.LOGS_PATH.exists():
    config.LOGS_PATH.mkdir()

# Configurar el formato del registro
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configurar el logger principal
# logging.getLogger("pyrogram").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(
    logging.DEBUG
)  # Configura el nivel más bajo para capturar todos los niveles en el logger

# Configurar el manejador para la consola
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Nivel para la consola
console_handler.setFormatter(logging.Formatter(log_format))

# Configurar el manejador para el archivo
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
log_filename = config.LOGS_PATH / f"log_{current_date}.log"
file_handler = TimedRotatingFileHandler(
    log_filename, when="midnight", backupCount=7, encoding="utf-8"
)
file_handler.setLevel(logging.DEBUG)  # Nivel para el archivo
file_handler.setFormatter(logging.Formatter(log_format))

# Agregar los manejadores al logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# # Ejemplo de cómo usar el logger
# logger.debug("Este es un mensaje de depuración")
# logger.info("Este es un mensaje informativo")
# logger.warning("Este es un mensaje de advertencia")
# logger.error("Este es un mensaje de error")
# logger.critical("Este es un mensaje crítico")
LOGGER = logger

system_operative = f"SO > {config.getOS()}"
LOGGER.info(system_operative)
if config.is_valid_version_python():
    LOGGER.info("Python version: %s", config.PYTHON_VERSION)
else:
    LOGGER.error("Python version must be at least 3.8")
    # LOGGER.error(
    #     "You MUST have a python version of at least 3.6! Multiple features depend on this. Bot quitting."
    # )
    exit() or quit(1)