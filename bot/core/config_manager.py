from ast import literal_eval
from importlib import import_module
from pathlib import Path

from telegram import __bot_api_version__
from telegram import __version__ as python_telegram_bot_ver

from bot import LOGGER

current_path = Path.cwd()


class Config:
    BOT_TOKEN = ""
    OWNER_ID = 0
    TELEGRAM_API = 0
    TELEGRAM_HASH = ""
    OWNER_USERNAME = ""
    AUTHORISED_USERS = []
    ID_CHAT = 0
    ID_CHAT_POSTS = 0
    HOST = ""
    API_OMDB = ""
    idthedb = 0
    API_KEY_AUTH = ""
    ACCESS_TOKEN_AUTH = ""

    # def __init__(self):
    #     # paths
    CURRENT_PATH = current_path / "bot"
    LOGS_PATH = CURRENT_PATH / "logs"

    BOT_NAME = ""
    python_telegram_bot_ver = python_telegram_bot_ver
    bot_api_ver = __bot_api_version__

    WEBHOOK = True
    DONATION_LINK = None
    PORT = 5000
    URL = None
    CERT_PATH = None
    # self.HOST = os.environ.get("HOST", "latinomegahd.net")
    WORKERS = 8  # Number of subthreads to use. This is the recommended amount - see for yourself what works best!

    ALLOW_EXCL = False  # Allow ! commands as well as /

    LANGUAGE = [
        "es-MX",
        "es-CO",
        "es-US",
        "es-ES",
        "es-AR",
        "es-CL",
        "es-PE",
        "es-VE",
        "es-EC",
        "es-UY",
        "es-BO",
        "es-PY",
        "es-HN",
        "es-SV",
        "es-NI",
        "es-PR",
        "en-US",
    ]

    URL_THEMOVIEDB = "https://api.themoviedb.org/3/"
    URL_IMAGE = "https://image.tmdb.org/t/p/original"
    NO_IMAGE = "poster/EnDtAZWUcAcgct_.jfif"
    # https: // www.themoviedb.org/talk/5aeaaf56c3a3682ddf0010de

    SEARCH_NAME_MOVIE = "search/movie"
    SEARCH_NAME_TV = "search/tv"
    SEARCH_ID_MOVIE = "movie/"
    SEARCH_ID_TV = "tv/"

    @classmethod
    def _convert(cls, key: str, value):
        if not hasattr(cls, key):
            raise KeyError(f"{key} is not a valid configuration key.")

        expected_type = type(getattr(cls, key))

        if value is None:
            return None

        if isinstance(value, expected_type):
            return value

        if expected_type is bool:
            return str(value).strip().lower() in {"true", "1", "yes"}

        if expected_type in [list, dict]:
            if not isinstance(value, str):
                raise TypeError(
                    f"{key} should be {expected_type.__name__}, got {type(value).__name__}"
                )

            if not value:
                return expected_type()

            try:
                evaluated = literal_eval(value)
                if not isinstance(evaluated, expected_type):
                    raise TypeError(
                        f"Expected {expected_type.__name__}, got {type(evaluated).__name__}"
                    )
                return evaluated
            except (ValueError, SyntaxError, TypeError) as e:
                raise TypeError(
                    f"{key} should be {expected_type.__name__}, got invalid string: {value}"
                ) from e

        try:
            return expected_type(value)
        except (ValueError, TypeError) as exc:
            raise TypeError(
                f"Invalid type for {key}: expected {expected_type}, got {type(value)}"
            ) from exc

    @classmethod
    def get(cls, key: str):
        return getattr(cls, key, None)

    @classmethod
    def set(cls, key: str, value) -> None:
        if not hasattr(cls, key):
            raise KeyError(f"{key} is not a valid configuration key.")

        converted_value = cls._convert(key, value)
        setattr(cls, key, converted_value)

    @classmethod
    def get_all(cls):
        return {
            key: getattr(cls, key)
            for key in cls.__dict__.keys()
            if not key.startswith("__") and not callable(getattr(cls, key))
        }

    @classmethod
    def _is_valid_config_attr(cls, attr: str) -> bool:
        if attr.startswith("__") or callable(getattr(cls, attr, None)):
            return False
        return hasattr(cls, attr)

    @classmethod
    def _process_config_value(cls, attr: str, value):
        if not value:
            return None

        converted_value = cls._convert(attr, value)

        if isinstance(converted_value, str):
            converted_value = converted_value.strip()

        return converted_value

    @classmethod
    def _load_from_module(cls) -> bool:
        try:
            settings = import_module("config")
        except ModuleNotFoundError:
            return False

        for attr in dir(settings):
            if not cls._is_valid_config_attr(attr):
                continue

            raw_value = getattr(settings, attr)
            processed_value = cls._process_config_value(attr, raw_value)

            if processed_value is not None:
                setattr(cls, attr, processed_value)

        return True

    @classmethod
    def _validate_required_config(cls) -> None:
        required_keys = ["BOT_TOKEN", "OWNER_ID", "TELEGRAM_API", "TELEGRAM_HASH"]

        for key in required_keys:
            value = getattr(cls, key)
            if isinstance(value, str):
                value = value.strip()
            if not value:
                raise ValueError(f"{key} variable is missing!")

    @classmethod
    def load(cls) -> None:
        if not cls._load_from_module():
            LOGGER.info(
                "Config module not found, loading from environment variables..."
            )
            cls._load_from_env()

        cls._validate_required_config()

    @classmethod
    def load_dict(cls, config_dict) -> None:
        for key, value in config_dict.items():
            if not hasattr(cls, key):
                continue

            processed_value = cls._process_config_value(key, value)

            if key == "USENET_SERVERS" and processed_value is None:
                processed_value = []

            if processed_value is not None:
                setattr(cls, key, processed_value)

        cls._validate_required_config()

    def set_bot_name(self, name):
        self.BOT_NAME = name
