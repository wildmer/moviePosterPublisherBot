from importlib import import_module

from .config_manager import Config


def load_settings():

    try:
        settings = import_module("config")
        config_file = {
            key: value.strip() if isinstance(value, str) else value
            for key, value in vars(settings).items()
            if not key.startswith("__")
        }
    except ModuleNotFoundError:
        config_file = {}

    config_dict = config_file
    Config.load_dict(config_dict)
