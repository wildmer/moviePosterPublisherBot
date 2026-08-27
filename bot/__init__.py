import sys

from bot.config import Config
from bot.core.logger_config import configure_logger

config = Config()

LOGGER = configure_logger(__name__)
log_filename = "log.log"

system_operative = f"SO > {config.getOS()}"
LOGGER.info(system_operative)

if config.is_valid_version_python():
    LOGGER.info("Python version: %s", config.PYTHON_VERSION)
else:
    LOGGER.error("Python version must be at least 3.8")
    # LOGGER.error(
    #     "You MUST have a python version of at least 3.6! Multiple features depend on this. Bot quitting."
    # )
    sys.exit() or sys.quit(1)
