# import codecs
# import asyncio
# import json

# import os
# import unicodedata
# from typing import List, Optional
from pathlib import Path

# import telegram
# from telegram import (  # ReplyKeyboardMarkup,; ReplyKeyboardRemove,; Update,; InlineKeyboardButton,; ParseMode
#     InlineKeyboardMarkup, InputMediaPhoto)
from . import LOGGER
from .core.config_manager import Config
from .core.telegram_manager import TgClient

Config.load()
# from bot.Config import HOST, NO_IMAGE, URL_IMAGE
# from bot.helpers.helper_funcs.filters import CustomFilters
# from telegram.ext.utils.promise import CallbackContext


# from bot.helpers.telegram_helper.decorators import is_authorised
# from bot.helpers.telegram_helper.msg_utils import (  # sendMarkup,
#     delete_message,
#     edit_message,
#     send_file,
#     send_message,
#     send_photo,
# )


from .core.startup import load_settings

# from telegram import Message, Chat, Update, Bot, User

# from telegram.error import Unauthorized, BadRequest, TimedOut, NetworkError, ChatMigrated, TelegramError



# from telegram.ext.dispatcher import run_async, DispatcherHandlerStop
# from telegram.utils.helpers import escape_markdown

# from telegram.message import Message
# from telegram.update import Update

# from telegram.ext import Updater
# from telegram import InputFile


def make_folder(folder_path: str) -> None:
    """
    Crea una carpeta en la ruta especificada.

    Args:
        folder_path (str): La ruta de la carpeta a crear.

    Returns:
        None
    """
    Path(folder_path).mkdir(parents=True, exist_ok=True)  # Crea la carpeta si no existe


def main():
    # config
    load_settings()
    TgClient.start_bot()


if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: ")
    make_folder("tv")
    make_folder("movie")
    make_folder("poster")

    main()

    # print(read_file('movie', '884605'))
    # posst("tv", 1396, update, context)

    # read_file('tv', '615')
    # tmdb = TheMovieDB("Cars", "2006-06-08")
    # tmdb = TheMovieDB("O Amor Dá Voltas", "2022-12-22")
    # tmdb = TheMovieDB("Hounded", "2022-10-21")

    # tmdb.search_movies()
    # print(tmdb.search_movies())

    # tmdb = TheMovieDB("Adventure Time", "2010-04-05")
    # # tmdb = TheMovieDB("Sex Education", "2019-01-11")
    # # print(tmdb.search_tv_shows())
    # tmdb.search_tv_shows()
    # data_media = tmdb.search_season_tv_shows(1)
    # create_file(f'tv/{data_media["_id"]}.json', data_media)

    # create_file('movies/test.txt')
    # data_scrap = scrap_url('https://www.latinomegahd.net/futurama-serie-de-tv-temporada-10-2013-latino-hd-dsnp-web-dl-1080p/')
    # print(scrap_url('https://www.latinomegahd.net/sonrie-2022-latino-ultrahd-hdr-bdremux-2160p/'))
    # data_scrap = scrap_url('https://www.latinomegahd.net/amenaza-bajo-el-agua-no-podras-escapar-2020-latino-hd-brrip-1080p/')
    # data_scrap = scrap_url('https://www.latinomegahd.net/sonrie-2022-latino-ultrahd-hdr-bdremux-2160p/')
    # tmdb = TheMovieDB(data_scrap["original_title"], data_scrap["release_date"])
    # tmdb.search_movies()
    # create_file(f'movie/884605.json')

# TODO: CRear boton para cerrar el bot enviar los logs
