import logging
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# Constantes
LOG_FORMAT = "%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s"
LOG_LEVEL_CONSOLE = logging.INFO
LOG_LEVEL_FILE = logging.DEBUG
LOGS_DIR = Path("logs")


def configure_logger(name: str = __name__) -> logging.Logger:
    """
    Configura y retorna un logger con salida a consola y archivo rotativo diario.

    Args:
        name (str): Nombre del logger. Por defecto es __name__.

    Returns:
        logging.Logger: Instancia del logger configurado.
    """
    # Asegurar que el directorio de logs exista
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Crear el logger
    logger = logging.getLogger(name)
    # logging.getLogger("pyrogram").setLevel(logging.ERROR)
    logger.setLevel(logging.DEBUG)
    # Configura el nivel más bajo para capturar todos los niveles en el logger

    # Evitar agregar handlers múltiples si ya está configurado
    if logger.hasHandlers():
        return logger

    # Manejador para la consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL_CONSOLE) # Nivel para la consola
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    # Manejador para archivo rotativo diario
    current_date = datetime.now(timezone.utc).date()
    # current_date = date.today().strftime("%Y-%m-%d")
    log_filename = LOGS_DIR / f"log_{current_date}.log"

    file_handler = TimedRotatingFileHandler(
        filename=log_filename, when="midnight", backupCount=7, encoding="utf-8"
    )
    file_handler.setLevel(LOG_LEVEL_FILE)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    # Agregar manejadores al logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# # Ejemplo de cómo usar el logger
# logger.debug("Este es un mensaje de depuración")
# logger.info("Este es un mensaje informativo")
# logger.warning("Este es un mensaje de advertencia")
# logger.error("Este es un mensaje de error")
# logger.critical("Este es un mensaje crítico")