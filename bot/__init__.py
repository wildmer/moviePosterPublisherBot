from sys import exit, platform, version_info

from bot.core.logger_config import configure_logger

LOGGER = configure_logger(__name__)
log_filename = "log.log"  # quitar esto ya que ahora es dinamico submodulizar


PYTHON_VERSION = f"{version_info.major}.{version_info.minor}.{version_info.micro}"


def getOS():
    if platform == "linux" or platform == "linux2":
        return "Linux"
    elif platform == "darwin":
        return "OS X"
    elif platform == "win32":
        return "Windows"
    else:
        return platform
        # return "Sorry, operating system not supported"
    # return sys.platform


system_operative = f"SO > {getOS()}"

LOGGER.info(system_operative)


def is_valid_version_python():
    if version_info.major < 3 or int(version_info.minor) < 8:
        return False
    return True


if is_valid_version_python():
    LOGGER.info("Python version: %s", PYTHON_VERSION)
else:
    LOGGER.error("Python version must be at least 3.8")
    # LOGGER.error(
    #     "You MUST have a python version of at least 3.6! Multiple features depend on this. Bot quitting."
    # )
    exit() # or quit(1)
